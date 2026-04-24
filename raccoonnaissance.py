import cloudscraper
from rich import print
from rich.progress import track
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json

# ===================== CONFIG =====================

MAX_THREADS = 10
RETRY = 2
TIMEOUT = 15

# ===================== SCRAPER =====================

scraper = cloudscraper.create_scraper()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
}

# ===================== EMAIL CHECKER SITES (DICTIONARY - MUDAH DITAMBAH) =====================
# FORMAT: "Nama Situs": {"method": "GET/POST", "url": "url_pattern", "params/data": {...}, "success_indicator": "text/status_code/keyword"}
# Ganti {email} dengan email target

email_sites_config = {
    "Instagram": {
        "method": "POST",
        "url": "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/",
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        "data": {"email": "{email}"},
        "check_type": "text",
        "success_condition": "email_is_taken"
    },
    "GitHub": {
        "method": "GET",
        "url": "https://github.com/signup_check/email",
        "params": {"email": "{email}"},
        "check_type": "json",
        "success_condition": "result:taken"
    },
    "Twitter/X": {
        "method": "GET",
        "url": "https://api.twitter.com/i/users/email_available.json",
        "params": {"email": "{email}"},
        "check_type": "json",
        "success_condition": "taken:true"
    },
    "Spotify": {
        "method": "GET",
        "url": "https://www.spotify.com/id/signup/check/email/",
        "params": {"email": "{email}"},
        "check_type": "text",
        "success_condition": "already taken"
    },
    "Adobe": {
        "method": "GET",
        "url": "https://auth.services.adobe.com/signup/v2/users/email",
        "params": {"email": "{email}"},
        "check_type": "status_code",
        "success_condition": 409
    },
    # ========== TAMBAHKAN SITUS BARU DI SINI ==========
    # "NamaSitusBaru": {
    #     "method": "GET",
    #     "url": "https://contoh.com/check/{email}",
    #     "params": {"email": "{email}"},
    #     "check_type": "text",
    #     "success_condition": "email already registered"
    # },
}

def check_single_email(email, site_name, site_config):
    """Fungsi universal untuk memeriksa email di satu situs berdasarkan konfigurasi"""
    try:
        # Siapkan URL dan parameter
        url = site_config["url"]
        params = site_config.get("params", {})
        data = site_config.get("data", {})
        headers_req = site_config.get("headers", headers.copy())
        
        # Ganti placeholder {email} dengan email target
        url = url.replace("{email}", email)
        if params:
            for key in params:
                if isinstance(params[key], str):
                    params[key] = params[key].replace("{email}", email)
        if data:
            for key in data:
                if isinstance(data[key], str):
                    data[key] = data[key].replace("{email}", email)
        
        method = site_config["method"].upper()
        
        # Eksekusi request sesuai method
        if method == "GET":
            r = scraper.get(url, headers=headers_req, params=params, timeout=TIMEOUT)
        elif method == "POST":
            r = scraper.post(url, headers=headers_req, params=params, data=data, timeout=TIMEOUT)
        else:
            return None
        
        check_type = site_config["check_type"]
        success_condition = site_config["success_condition"]
        
        # Cek berdasarkan tipe
        if check_type == "status_code":
            return r.status_code == success_condition
        
        elif check_type == "text":
            text_lower = r.text.lower()
            condition_lower = success_condition.lower()
            return condition_lower in text_lower
        
        elif check_type == "json":
            try:
                json_data = r.json()
                if ":" in success_condition:
                    key, expected = success_condition.split(":", 1)
                    # Konversi tipe data
                    if expected.lower() == "true":
                        expected = True
                    elif expected.lower() == "false":
                        expected = False
                    elif expected.isdigit():
                        expected = int(expected)
                    
                    # Navigasi nested JSON (contoh: data.user.exists)
                    keys = key.split(".")
                    value = json_data
                    for k in keys:
                        if isinstance(value, dict) and k in value:
                            value = value[k]
                        else:
                            return False
                    return value == expected
            except:
                return False
        
        return False
        
    except Exception:
        return None

def run_email_check(email):
    """Fungsi utama untuk memeriksa email di semua situs yang terkonfigurasi"""
    print(f"[yellow][*] Checking email:[/yellow] [bold]{email}[/bold]\n")
    
    email_results = []
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_site = {
            executor.submit(check_single_email, email, site_name, config): site_name
            for site_name, config in email_sites_config.items()
        }
        
        for future in as_completed(future_to_site):
            site_name = future_to_site[future]
            result = future.result()
            
            if result is True:
                print(f"[green][+] {site_name:15}[/green] : EMAIL REGISTERED!")
                email_results.append(f"[FOUND] {site_name} -> {email} is registered")
            elif result is False:
                print(f"[cyan][-] {site_name:15}[/cyan] : EMAIL NOT REGISTERED")
            else:
                print(f"[red][!] {site_name:15}[/red] : CHECK FAILED")
    
    if email_results:
        with open("email_results.txt", "a") as f:
            f.write(f"\n=== {email} ===\n")
            for line in email_results:
                f.write(line + "\n")
    
    return email_results

def run_email_dl(file_path):
    """Mode dictionary list untuk email"""
    try:
        with open(file_path, "r") as f:
            emails = [line.strip() for line in f if line.strip()]
        
        print(f"[bold cyan][*] Loaded {len(emails)} emails from {file_path}[/bold cyan]")
        
        for email in emails:
            print(f"\n[bold yellow]--- Processing: {email} ---[/bold yellow]")
            run_email_check(email)
            time.sleep(1)  # Delay to avoid rate limiting
            
    except FileNotFoundError:
        print("[red][-] File not found[/red]")

# ===================== CHECK FUNCTION =====================

def check_username(url):
    for attempt in range(RETRY):
        try:
            r = scraper.get(url, headers=headers, timeout=TIMEOUT)

            if r.status_code == 200:
                text = r.text.lower()

                if any(x in text for x in [
                    "not found",
                    "user not found",
                    "page doesn't exist",
                    "this account doesn't exist",
                    "try searching for another",
                    "nobody here"
                ]):
                    return False, 200

                return True, 200

            elif r.status_code == 404:
                return False, 404

            else:
                return "ERROR", r.status_code

        except Exception:
            if attempt < RETRY - 1:
                time.sleep(1)
            else:
                return "TIMEOUT", None

# ===================== DL MODE =====================

def run_dl(file_path):
    try:
        with open(file_path, "r") as f:
            usernames = [line.strip() for line in f if line.strip()]

        print(f"[bold cyan][*] Loaded {len(usernames)} usernames from {file_path}[/bold cyan]")

        for username in usernames:
            run_scan(username)

    except FileNotFoundError:
        print("[red][-] File not found[/red]")

# ===================== CORE SCANNER =====================

def run_scan(username):

    sites = {
        "GitHub": f"https://github.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "Twitter/X": f"https://twitter.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Tiktok": f"https://www.tiktok.com/@{username}",
        "Deviantart": f"https://www.deviantart.com/{username}",
        "Facebook": f"https://www.facebook.com/{username}",
        "FurAffinity": f"https://www.furaffinity.net/user/{username}/",
        "Carrd": f"https://{username}.carrd.co",
        "Strawpage": f"https://{username}.straw.page",
        "Linktree": f"https://linktr.ee/{username}",
        "Twitch": f"https://m.twitch.tv/{username}/home",
        "Youtube": f"https://m.youtube.com/@{username}",
        "Pinterest": f"https://id.pinterest.com/{username}/",
        "Bluesky": f"https://bsky.app/profile/{username}",
        "Patreon": f"https://www.patreon.com/{username}"
      }

    print(f"[yellow][*] Investigating:[/yellow] [bold]{username}[/bold]\n")

    results = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_site = {
            executor.submit(check_username, url): (name, url)
            for name, url in sites.items()
        }

        for future in track(as_completed(future_to_site), total=len(future_to_site)):
            name, url = future_to_site[future]
            result, code = future.result()

            if result is True:
                print(f"[green][+] {name:12}[/green] : FOUND! [blue]({url})[/blue]")
                results.append(f"[FOUND] {name} -> {url}")

            elif result is False:
                print(f"[cyan][-] {name:12}[/cyan] : NOT FOUND")

            elif result == "ERROR":
                print(f"[red][!] {name:12}[/red] : ERROR [CODE: {code}]")

            else:
                print(f"[red][?] {name:12}[/red] : TIMEOUT")

    # Save result
    if results:
        with open("results.txt", "a") as f:
            f.write(f"\n=== {username} ===\n")
            for line in results:
                f.write(line + "\n")

# ===================== UI =====================

os.system("jp2a --invert /sdcard/pictures/Screenshot/Screenshot_20260418-211809.png")

print("[bold cyan]" + "="*75 + "[/bold cyan]")
print("                           RACCOONNAISSANCE                ")
print("                      Version 2.0.0 (PROTOTYPE)            ")
print("             Created by [bold cyan]Kenn Vangelis[/bold cyan], powered by cloudscraper")
print("[yellow][NOTE] Pls use this tools with ethics UwU[/yellow]")
print("[bold cyan]" + "="*75 + "[/bold cyan]")

print("\nMode:")
print("[1] Single username")
print("[2] Dictionary list (dl) for username")
print("[3] Single email checker")
print("[4] Dictionary list for email")

mode = input("Select mode (1/2/3/4): ")

# ===================== MODE HANDLER =====================

if mode == "2":
    file_path = input("Enter file (example: usernames.txt): ")
    run_dl(file_path)

elif mode == "3":
    email = input("Enter email target: ")
    print("[yellow][*] Wait! Checking email now...[/yellow]")
    run_email_check(email)

elif mode == "4":
    file_path = input("Enter email list file (example: emails.txt): ")
    run_email_dl(file_path)

else:
    username = input("Enter username target: ")

    print("[yellow][*] Wait! we've been collecting cookies![/yellow]")

    scraper.get("https://www.furaffinity.net")
    scraper.get("https://www.facebook.com")
    scraper.get("https://linktr.ee/")

    run_scan(username)

print("\n[bold cyan]OUR RACCOONS MANAGED INVESTIGATE IT![/bold cyan]")
