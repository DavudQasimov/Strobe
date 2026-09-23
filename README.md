<h1 align="center">
  <img src="logo.png" width="20%" height="30%" style="vertical-align: middle;">
</h1>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com/?lines=Strobe;&font=Fira%20Code&center=true&width=380&height=50&duration=4000&pause=1000" alt="Example Usage - README Typing SVG">
</p>

# ⚡ Strobe — Credential Test & Brute-Force Orchestrator

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](#-installation--global-setup)

**Strobe** is a high-performance Python orchestrator and automated reporting wrapper around **THC-Hydra** and **Medusa**.

It simplifies credential testing across multiple network protocols, unifies command-line syntax disparities between underlying engines, and automatically generates structured **Markdown (`.md`)** or **Plain Text (`.txt`)** audit reports.

---

## 🚀 Key Features

* **Unified CLI Syntax:** No need to remember different flags or formats for Hydra and Medusa.
* **Multi-Engine Execution:** Run Hydra, Medusa, or both tools sequentially in a single command.
* **Automated Reporting:** Generates clean, timestamped audit logs containing raw commands, execution statuses, and sanitized outputs.
* **Complex Form Support:** Native parsing for HTTP POST/GET forms (`http-post-form`, `http-get-form`) without CLI escaping issues.
* **Global Access:** Built-in symbolic link setup for system-wide execution (`strobe`).

---

## 🛠️ Prerequisites

Ensure you have the following installed on your system:

* **Python 3.8+**
* **THC-Hydra** (`hydra` in system PATH)
* **Medusa** (`medusa` in system PATH)

On Debian / Ubuntu / Kali Linux:
```bash
sudo apt update && sudo apt install -y hydra medusa python3
📥 Installation & Global Setup
To run strobe (or asrx) as a system-wide command from any path in your terminal:

1. Clone the Repository & Set Execution Permissions
Bash
git clone https://github.com/DavudQasimov/Strobe.git
cd strobe
chmod +x strobe.py
2. Create a Global Symbolic Link
Create a symlink in /usr/local/bin so the operating system recognizes the command globally:

Bash
# Register as 'strobe'
sudo ln -s "$(pwd)/strobe.py" /usr/local/bin/strobe

3. Verify Installation
Open a new terminal shell in any random directory and run:

Bash
strobe -h
📖 CLI Argument Reference
Plaintext
usage: strobe [-h] -s SERVICE [SERVICE ...] [-l USER] [-L USERLIST]
              [-p PASSWORD] [-P PASSLIST] [--port PORT] [-t THREADS]
              [-report {md,txt}] [--only [{hydra,medusa} ...]]
              target
Flag / Option	Type	Description
target	Positional	Target IP address, domain, or hostname.
-s, --service	Required	Protocol or form specification (e.g., ssh, ftp, http-post-form).
-l, --user	Optional	Single username to test.
-L, --userlist	Optional	Path to wordlist containing target usernames.
-p, --password	Optional	Single password to test.
-P, --passlist	Optional	Path to wordlist containing passwords (rockyou.txt).
--port	Optional	Custom destination port number (1–65535).
-t, --threads	Optional	Number of parallel execution threads (Default: 4).
-report, --report	Optional	Output report format: md or txt (Default: md).
--only	Optional	Limit execution to specific tools: hydra or medusa.
💡 Usage Examples
1. Dual Engine Attack (Hydra + Medusa)
Sequential SSH password testing using a single username and password dictionary:

Bash
strobe 10.81.128.118 -s ssh -l root -P /usr/share/wordlists/rockyou.txt -t 16
2. Web HTTP POST Form (Hydra Only)
Brute-forcing an HTML login form with custom error parameters:

Bash
strobe 10.81.128.118 \
  -l admin \
  -P /usr/share/wordlists/rockyou.txt \
  -s http-post-form "/login:username=^USER^&password=^PASS^:Your username or password is incorrect." \
  --only hydra
3. Non-Standard Port Attack
Testing FTP on custom port 2121 using a username list and single password:

Bash
strobe 192.168.1.50 -s ftp -L usernames.txt -p Summer2026! --port 2121
4. Fast Password Spraying (Medusa Only)
Testing a single password across a wide list of corporate user accounts:

Bash
strobe 10.10.10.50 -s ssh -L users.txt -p Password123! -t 8 --only medusa
📊 Sample Output Report (strobe_report.md)
After execution, Strobe generates a clean Markdown report in your current directory:

Strobe Report
Field	Value
Target	10.81.128.118
Service	http-post-form /login:username=^USER^&password=^PASS^:Your username or password is incorrect.
Date	2026-09-23 19:00:00
1. Hydra - HTTP-POST-FORM Execution
Tool	/usr/bin/hydra
Command	hydra -l admin -P /usr/share/wordlists/rockyou.txt -t 4 -f -o - 10.81.128.118 http-post-form ...
Status	OK
Plaintext
[80][http-post-form] host: 10.81.128.118   login: admin   password: sunshine
1 of 1 target successfully completed, 1 valid password found
⚠️ Disclaimer
This tool is designed strictly for authorized penetration testing, red teaming, and educational security assessments. Unauthorized access attempts against targets without explicit written authorization are illegal. The author assumes no liability for misuse.

👤 Author & Contact
Davud Qasimov

LinkedIn: Davud Qasimov

Medium: https://medium.com/@qasimovdavud39

Gmail: qasimovdavud39@gmail.com

Discord: etozryx_13553
