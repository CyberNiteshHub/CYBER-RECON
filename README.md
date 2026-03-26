# 🕵️ CyberRecon - Advanced OSINT & Reconnaissance Toolkit

**A professional, local GUI-based Information Gathering tool for Ethical Hacking, Vulnerability Assessment, and Network Reconnaissance.**

> **Status:** Active | **Version:** 1.0 | **Last Updated:** March 2026

---

## 📋 Project Overview

CyberRecon is an **Advanced Reconnaissance Suite** designed for cybersecurity professionals and ethical hackers to perform comprehensive network and web application reconnaissance. Built with a dark cyberpunk interface, this tool consolidates multiple OSINT (Open Source Intelligence) techniques into a single, user-friendly platform.

This project demonstrates advanced skills in:
- Network socket programming & protocol understanding
- Multi-threaded concurrent operations
- Web framework development (Flask)
- Frontend & backend integration
- Cybersecurity tool development
- Professional UI/UX design

---

## 📌 Internship Information

**Program:** SYNTECXHUB Cybersecurity Virtual Internship  
**Intern:** Nitesh  
**Domain:** Cybersecurity - Reconnaissance & OSINT  
**Start Date:** March 25, 2026  
**Duration:** 1 Month  
**Project Type:** Week 1 - Advanced Cybersecurity Project  
**Difficulty Level:** Advanced (Exceeds Base Requirements)  
**Repository:** https://github.com/CyberNiteshHub/CYBER-RECON  
**Contact:** info@syntecxhub.com | +91 63937 80295  

*(Note: This section can be completely removed after internship completion)*

---

## ✨ Key Features

### 🔍 Reconnaissance Tools (12+)
- **Ping Test** - Latency checking & host availability
- **Traceroute** - Network path analysis & geo-tracing
- **DNS Records** - Deep DNS lookup with all record types
- **WHOIS Lookup** - Domain registration & ownership info
- **GeoIP Satellite Mode** - Geographic location of IP addresses
- **SSL/TLS Security Scanner** - Certificate analysis & security validation
- **Tech Stack Detector** - Identify technologies used by target
- **Hidden Admin Path Finder** - Common admin panel discovery
- **HTTP Headers Analysis** - Web server & technology detection
- **SQL Injection Vulnerability Scanner** - SQLI vulnerability detection
- **Nmap Deep Scan** - Network port scanning & service enumeration
- **Subnet Calculator** - CIDR & subnet network calculations
- **Page Link Extractor** - Web scraping & link enumeration

### 📊 Dashboard & Analytics
- **Real-Time Scan History** - Track all scans with timestamps
- **Vulnerability Statistics** - Count & categorize vulnerabilities
- **Risk Level Classification** - High/Medium/Low severity marking
- **Search Functionality** - Quick lookup of previous scans
- **Data Export** - JSON & CSV format exports
- **Professional Reporting** - Auto-generated reports

### 🎨 User Interface
- **Dark Cyberpunk Theme** - Modern hacker aesthetic
- **Responsive Design** - Works on desktop & tablets
- **One-Click Execution** - No complex command-line knowledge needed
- **Real-Time Output** - Live scanning results display

---

## 🛠️ Technologies Used

### Backend
- **Language:** Python 3.8+
- **Framework:** Flask (Web Framework)
- **Libraries:**
  - `socket` - Network socket programming
  - `subprocess` - Execute system commands
  - `requests` - HTTP requests for API calls
  - `dnspython` - DNS query handling
  - `geoip2` - GeoIP lookups
  - `threading` - Concurrent scanning operations

### Frontend
- **HTML5** - Structure
- **CSS3** - Cyberpunk styling
- **JavaScript (Vanilla)** - Interactivity & real-time updates

### Tools & Dependencies
- **Nmap** - Network mapping & port scanning
- **Traceroute** - Network diagnostics
- **System commands** - dig, whois, curl

---

## 🚀 Installation & Setup

### Windows

**Prerequisites:**
- Python 3.8 or higher
- Nmap installed ([Download](https://nmap.org/download.html))
- Git installed

**Steps:**
```bash
# Clone the repository
git clone https://github.com/CyberNiteshHub/CYBER-RECON.git
cd CYBER-RECON

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

**Browser Access:**
```
http://localhost:5000
```

Or simply double-click `run_windows.bat`

---

### Linux / Kali Linux

**Prerequisites:**
- Python 3.8+
- Nmap
- Git

**Steps:**
```bash
# Clone the repository
git clone https://github.com/CyberNiteshHub/CYBER-RECON.git
cd CYBER-RECON

# Make scripts executable
chmod +x run_linux.sh
chmod +x install_dependencies.sh

# Install system dependencies (optional)
sudo ./install_dependencies.sh

# Install Python dependencies
pip install -r requirements.txt

# Run the application
./run_linux.sh
```

**Or directly:**
```bash
python app.py
```

**Browser Access:**
```
http://localhost:5000
```

---

## 📖 How to Use

### Step 1: Launch Application
```bash
python app.py
```
Browser automatically opens to `http://localhost:5000`

### Step 2: Select Target
Enter target in the input field:
- **Domain:** `example.com`
- **URL:** `http://example.com`
- **IP Address:** `192.168.1.1`
- **IP Range:** `192.168.1.0/24`

### Step 3: Choose Tool
Select from dropdown menu (12+ tools available)

### Step 4: Run Scan
Click **"RUN TOOL"** button

### Step 5: View Results
Results appear in real-time in the dashboard

### Step 6: Export & Report
- **Export JSON:** Machine-readable format
- **Export CSV:** Spreadsheet-compatible format

---

## 📁 File Structure

```
CYBER-RECON/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
│
├── templates/
│   ├── index.html             # Main scanning interface
│   └── dashboard.html         # Results dashboard
│
├── static/
│   ├── css/
│   │   ├── style.css          # Cyberpunk styling
│   │   └── dashboard.css      # Dashboard styling
│   │
│   └── js/
│       ├── main.js            # Core functionality
│       └── dashboard.js       # Dashboard management
│
├── tools/
│   ├── ping_scan.py           # Ping utility
│   ├── traceroute_scan.py     # Traceroute implementation
│   ├── dns_lookup.py          # DNS queries
│   ├── whois_lookup.py        # WHOIS info
│   ├── geoip_scan.py          # GeoIP detection
│   ├── ssl_scanner.py         # SSL/TLS analysis
│   ├── tech_detector.py       # Tech stack detection
│   ├── nmap_scanner.py        # Nmap integration
│   ├── sqli_scanner.py        # SQL Injection detection
│   └── admin_finder.py        # Admin path discovery
│
├── data/
│   ├── scan_history.json      # Scan history storage
│   └── reports/               # Generated reports
│
├── run_windows.bat            # Windows launcher
└── run_linux.sh               # Linux launcher
```

---

## 🔒 Security & Ethical Use

### ⚠️ IMPORTANT DISCLAIMER

```
This tool is intended for EDUCATIONAL PURPOSES ONLY.

UNAUTHORIZED USE IS ILLEGAL:
- Do NOT scan targets without written permission
- Do NOT use for malicious purposes
- Do NOT access systems you don't own

AUTHORIZED USE CASES:
- Personal network testing
- Authorized penetration testing (with permission)
- Educational learning & practice
- Bug bounty programs (with scope permission)

By using this tool, you agree to follow all applicable laws 
and ethical guidelines in your jurisdiction.
```

### 🛡️ Best Practices
- Always get written authorization before testing
- Document all activities with timestamps
- Use responsible disclosure for vulnerabilities
- Respect rate limits & network resources
- Never use on production systems without approval

---

## 📦 Dependencies

See `requirements.txt` for full list:

```
Flask==2.3.0
dnspython==2.3.0
requests==2.31.0
geoip2==4.7.0
reportlab==4.0.0
```

Install all:
```bash
pip install -r requirements.txt
```

---

## 🎊 Features Showcase

### Real-Time Dashboard
- Live scan results with timestamps
- Vulnerability counting & categorization
- Risk severity levels (High/Medium/Low)
- Search & filter capabilities
- Export scan data to JSON/CSV

### Multiple Tools in One
Instead of running separate commands, all tools integrated:
```
Traditional Way:
$ nmap scanme.nmap.org
$ whois scanme.nmap.org
$ dig scanme.nmap.org
$ traceroute scanme.nmap.org

CyberRecon Way:
1. Enter target: scanme.nmap.org
2. Select tool from dropdown
3. Click "Run Tool"
4. Get results in beautiful dashboard
```

---

## 🔄 Workflow Example

```
Target: example.com
├─ Step 1: Ping Test
│  └─ Result: Host is alive (25ms latency)
│
├─ Step 2: WHOIS Lookup
│  └─ Result: Registrant info, nameservers
│
├─ Step 3: DNS Records
│  └─ Result: A, MX, TXT, NS records
│
├─ Step 4: Tech Stack Detector
│  └─ Result: Server, CMS, Frontend frameworks
│
├─ Step 5: SSL/TLS Scanner
│  └─ Result: Certificate validity, encryption strength
│
├─ Step 6: HTTP Headers
│  └─ Result: Server info, security headers
│
└─ Step 7: Export Results
   └─ Result: JSON/CSV file generated
```

---

## 🌐 API Integration

Tools that use external APIs:
- **GeoIP:** MaxMind GeoIP2
- **Tech Stack:** Whatrack/Built With API
- **DNS:** Google Public DNS
- **WHOIS:** IANA WHOIS servers

---

## 🚦 System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| Python | 3.8 | 3.10+ |
| RAM | 2 GB | 4 GB+ |
| Disk | 500 MB | 1 GB+ |
| Nmap | Latest | Latest |
| OS | Windows/Linux | Linux/Kali |

---

## 📝 Usage Examples

### Example 1: Quick Domain Scan
```
Target: google.com
Tool: Ping Test
Output: Host alive, latency 45ms
```

### Example 2: SSL Certificate Check
```
Target: github.com
Tool: SSL/TLS Security Scanner
Output: 
  - Valid until: 2025-03-20
  - Issuer: DigiCert
  - Grade: A+
```

### Example 3: Subnet Planning
```
Target: 192.168.0.0/24
Tool: Subnet Calculator
Output:
  - Total IPs: 256
  - Usable: 254
  - Network: 192.168.0.0
  - Broadcast: 192.168.0.255
```

---

## 🔧 Configuration

### Change Port
Edit `app.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Change 5000 to desired port
```

### Enable HTTPS
Add SSL certificate support:
```python
app.run(ssl_context='adhoc')  # Requires pyopenssl
```

### Customize Theme
Edit `static/css/style.css` for color scheme changes

---

## 📊 Data Storage

- **Scan History:** Stored in `data/scan_history.json`
- **Reports:** Saved in `data/reports/` directory
- **Exports:** JSON & CSV formats in downloads folder

---

## 🌟 Why Use CyberRecon?

✅ **All-in-One Tool** - 12+ reconnaissance tools in one interface  
✅ **No CLI Knowledge Needed** - GUI for everyone  
✅ **Professional Output** - Beautiful dashboard & reports  
✅ **Fast & Efficient** - Multi-threaded scanning  
✅ **Educational** - Learn networking & cybersecurity concepts  
✅ **Ethical** - Built with security best practices  
✅ **Open Source** - Transparent, auditable code  

---

## 📚 Learn More

### Networking Concepts
- TCP/IP Stack fundamentals
- DNS resolution process
- Network routing & hops
- Port scanning techniques
- SSL/TLS certificates

### Cybersecurity Skills
- OSINT (Open Source Intelligence)
- Reconnaissance methodology
- Vulnerability identification
- Ethical hacking practices
- Responsible disclosure

### Programming Concepts
- Socket programming
- Multithreading in Python
- Web framework development
- Frontend-Backend integration
- API design & integration

---

## 🎯 Use Cases

1. **Security Professionals** - Quick reconnaissance toolkit
2. **Students** - Learn networking & cybersecurity
3. **Bug Bounty Hunters** - Fast information gathering
4. **Penetration Testers** - Initial reconnaissance phase
5. **Network Administrators** - Network diagnostics
6. **Developers** - Check own infrastructure

---

## 📖 Quick Reference

| Command | Purpose |
|---------|---------|
| `python app.py` | Start application |
| `pip install -r requirements.txt` | Install dependencies |
| `http://localhost:5000` | Access web interface |
| `run_windows.bat` | Auto-launch on Windows |
| `./run_linux.sh` | Auto-launch on Linux |

---

## 🔗 Important Links

**GitHub Repository:**
```
https://github.com/CyberNiteshHub/CYBER-RECON
```

**Nmap Documentation:**
```
https://nmap.org/
```

**Network Tools:**
- Ping: Built-in OS utility
- Traceroute: Built-in OS utility
- DNS: dnspython library
- WHOIS: whois command-line tool

---

## 📄 License

This project is provided as-is for educational and authorized security testing purposes only.

---

## 🎊 Version History

**v1.0 - March 2026**
- ✅ 12+ reconnaissance tools integrated
- ✅ Real-time dashboard with analytics
- ✅ JSON/CSV export functionality
- ✅ Dark cyberpunk UI
- ✅ Multi-platform support (Windows, Linux)

---

**Ready to use!** Happy hacking ethically! 🚀🔐
