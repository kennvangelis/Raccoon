# 🦝 Raccoonnaissance

> Simple OSINT tool to find usernames and emails across platforms — ethically.

![Version](https://img.shields.io/badge/version-2.1.0--prototype-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-yellow)

Created by [Kenn Vangelis](https://github.com/kennvangelis), powered by `cloudscraper`.

---

## ⚠️ ETHICAL USE ONLY

Please use this tool responsibly. Do not harass, stalk, or violate privacy laws. This is for educational, security research, and authorized penetration testing purposes only.

---

## 📦 Features

- Single username/email lookup
- Dictionary-based bulk scanning (new in v2.1!)
- Multi-platform support: Twitter, Instagram, Adobe, Spotify, GitHub (+ more coming!)
- Built-in rate limiting & Cloudflare bypass via `cloudscraper`
- Color-coded output for quick analysis

---

## 🛠️ Installation

```bash
git clone https://github.com/kennvangelis/Raccoon.git
cd Raccoon
pip install -r requirements.txt  # if you add one later
python raccoonnaissance.py
```

*(Optional: Add requirements.txt with `cloudscraper`, `requests`, etc.)*

---

## 🧪 Usage Example

```bash
$ python raccoonnaissance.py
Select mode (1/2/3/4): 3
Enter email target: kennvangelis@gmail.com
[*] Wait! Checking email now...
[+] Twitter     : EMAIL REGISTERED!
[-] Instagram   : EMAIL NOT REGISTERED
...
```

---

## 🔄 Changelog

### v2.1.0 (April 24, 2026)
- Added email dictionary list mode (#4)
- Improved error handling for failed checks
- Ethical reminder banner added

### v2.0.0
- Initial public release
- Single username/email checker
- ASCII raccoon logo 😄

---

## 🤝 Contributing

Pull requests welcome! Please open an issue first to discuss major changes.

---

## 📜 License

MIT License — feel free to fork, modify, and share (with credit).

---

## 💬 Support / Feedback

Found a bug? Have a feature idea? Open an [issue](https://github.com/kennvangelis/Raccoon/issues)!

Or DM me on Twitter/X: [@kennvangelis](https://twitter.com/kennvangelis) *(if applicable)*

---

> “Our raccoons managed investigate it!” — The Raccoon Team 🦝
