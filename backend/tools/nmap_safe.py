import nmap
import socket
import datetime
import requests
import sys

def check_web_status(target):
    """
    Step 1: Check HTTP/HTTPS manually.
    Reliable method to find web ports even if firewall blocks ICMP.
    """
    found_ports = []
    checks = [('http://', 80), ('https://', 443), ('http://', 8080), ('https://', 8443)]
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) CyberRecon/4.0'}

    for proto, port in checks:
        try:
            url = f"{proto}{target}"
            r = requests.get(url, headers=headers, timeout=2, allow_redirects=True)
            
            server = r.headers.get('Server', 'Unknown Web Server')
            found_ports.append({
                'port': port,
                'proto': 'tcp',
                'state': 'open',
                'name': 'http' if port in [80, 8080] else 'https',
                'version': f"{server} (Web Verified)",
                'reason': f"HTTP Status: {r.status_code}"
            })
        except:
            pass
    return found_ports

def run(target):
    scan_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # --- REPORT HEADER (Clean Design) ---
    output_text = ""
    output_text += f"╔{'═'*70}╗\n"
    output_text += f"║  ADVANCED DEEP SCANNER v4.0 (ROOT ACCESS)   |  {scan_time:<19} ║\n"
    output_text += f"╠{'═'*70}╣\n"
    output_text += f"║  TARGET   : {target:<53}  ║\n"
    output_text += f"║  MODE     : Full Recon (SYN Scan + OS Detect + Versions)             ║\n"
    output_text += f"╚{'═'*70}╝\n\n"

    try:
        # 1. Resolve IP
        target_ip = target
        try:
            if any(c.isalpha() for c in target):
                target_ip = socket.gethostbyname(target)
            output_text += f"[*] Target Resolved: {target} -> {target_ip}\n"
        except:
            return {"ok": False, "error": f"DNS Error: Could not resolve {target}."}

        # 2. Nmap Configuration
        nm = nmap.PortScanner()
        
        # --- 🔥 THE POWERFUL COMMAND ---
        # -sS : SYN Scan (Stealthy & Fast) - Requires Root/Sudo
        # -sV : Version Detection (Finds exact software versions)
        # -O  : OS Detection (Guesses Linux/Windows/Android)
        # -Pn : Treat Host as Online (Skip Ping)
        # -T4 : Aggressive Timing (Speed optimized)
        # --version-intensity 5 : Aggressive version checking
        args = '-sS -sV -O -Pn -T4 --version-intensity 5'
        
        output_text += "[*] Initiating Deep Scan (Top 1000 Ports)... Please Wait...\n"
        
        # 3. Scanning
        try:
            # Sudo zaroori hai -sS aur -O ke liye
            nm.scan(target_ip, arguments=args)
        except Exception as e:
            output_text += f"[!] Root Scan Failed (trying fallback): {e}\n"
            # Fallback to Connect Scan (-sT) if root fails
            nm.scan(target_ip, arguments='-sT -Pn -sV --version-intensity 3')

        # 4. Parsing Results
        scan_data = []
        os_match = "Unknown OS"
        device_type = "General Purpose"

        if target_ip in nm.all_hosts():
            host_data = nm[target_ip]
            
            # --- Extract OS Details ---
            if 'osmatch' in host_data and host_data['osmatch']:
                # Get the most accurate match
                os_match = f"{host_data['osmatch'][0]['name']} (Accuracy: {host_data['osmatch'][0]['accuracy']}%)"
                if 'osclass' in host_data['osmatch'][0]:
                    device_type = host_data['osmatch'][0]['osclass'][0].get('type', 'Unknown')

            # --- Extract Port Details ---
            for proto in host_data.all_protocols():
                lport = host_data[proto].keys()
                for port in sorted(lport):
                    svc = host_data[proto][port]
                    if svc['state'] == 'open':
                        scan_data.append({
                            'port': port,
                            'proto': proto,
                            'state': 'open',
                            'name': svc.get('name', 'unknown'),
                            'version': f"{svc.get('product','')} {svc.get('version','')} {svc.get('extrainfo','')}".strip(),
                            'reason': svc.get('reason', 'syn-ack')
                        })

        # 5. Fallback Web Check (Merge)
        web_ports = check_web_status(target)
        existing_ports = [p['port'] for p in scan_data]
        for wp in web_ports:
            if wp['port'] not in existing_ports:
                scan_data.append(wp)
                scan_data.sort(key=lambda x: x['port'])

        # --- FINAL OUTPUT GENERATION ---

        if not scan_data:
             return {
                "ok": False, 
                "error": "Target appears completely locked down (Firewall Detected).\nTry scanning a standard domain."
            }

        # SYSTEM INFO BOX
        output_text += f"\n┌──[ SYSTEM INTELLIGENCE ]{'─'*47}\n"
        output_text += f"│  Operating System : {os_match}\n"
        output_text += f"│  Device Type      : {device_type}\n"
        output_text += f"│  Total Open Ports : {len(scan_data)}\n"
        output_text += f"└{'─'*70}\n\n"

        # PORTS TABLE
        # No ANSI codes here, just clean text layout
        for item in scan_data:
            port = item['port']
            proto = item['proto'].upper()
            service = item['name'].upper()
            version = item['version'] if item['version'] else "Version Unknown"
            reason = item['reason']

            output_text += f"│\n"
            output_text += f"├──▶ PORT {port:<5} /{proto:<3} [ {service} ]\n"
            output_text += f"│    State   : OPEN (Accessible)\n" # Fixed Visual Glitch
            output_text += f"│    Version : {version}\n"
            output_text += f"│    Details : {reason}\n"
            output_text += f"│\n"
            output_text += f"└{'─'*70}\n"

        output_text += "\n[*] Advanced Reconnaissance Completed."

        return {"ok": True, "data": output_text}

    except Exception as e:
        return {"ok": False, "error": f"Scanner Error: {str(e)}"}