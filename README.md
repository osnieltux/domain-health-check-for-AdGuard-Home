# domain-health-check-for-AdGuard-Home
Given a list of domains, check which ones return a 200 OK web response. Additionally, enable manual browser verification of the content to generate a new list for use in AdGuard.

This repository contains lists of domains for filtering purposes. It does not host or promote adult content.

---

The idea came about while using 1.1.1.3 (Cloudflare Family) as a DNS to block content and noticing that some adult sites are still accessible. This led me to check the old 'Shalla Blacklists.' However, given there are over 803000 sites to verify, to see if they are still active or not yet blocked. I decided to build a tool to filter exactly what I need. (I used some AI assistance for modeling, so it’s not built 100% from scratch; I’m short on time, and AI is your friend!)

---
## If you just want to use my list, simply add it to your AdGuard Home.
```bash
https://raw.githubusercontent.com/osnieltux/domain-health-check-for-AdGuard-Home/refs/heads/main/list_checked.txt
```

---

# Dependencies
  - [Python](https://www.python.org)
  - [brotab](https://github.com/balta2ar/brotab)

## Install 
```bash
virtualenv .venv
source .venv/bin/activate 
pip install -r requirements.txt
```

## Usage
  - Create a "toCheck.txt" file with the domains to check separated by line breaks.
  - Run main.py.
  - Run browser.sh, This will start opening tabs in your browser. If you want to block it, press Enter; otherwise, open any other tab. You will then have a file ready to use in AdGuard called: list_checked.txt

---

### Just for Linux


### 💸 Sponsors
  [![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/osnieltux)