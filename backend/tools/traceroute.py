import platform
import subprocess
import re
import requests
import shutil
import sys

# --- 🌍 HELPER: Get Location for an IP ---
def get_ip_location(ip):
    # Private IPs (Localhost/Router/Private Network) ke liye lookup skip karein
    if ip.startswith(("192.168.", "10.", "172.", "127.", "0.")):
        return "Local Network", "Private Address"
    
    try:
        # Fast API call (Timeout 1.5s taaki traceroute slow na ho)
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode,city,isp", timeout=1.5)
        if response.status_code == 200:
            data = response.json()
            # Format: City, Country
            loc = f"{data.get('city', '?')}, {data.get('countryCode', '?')}"
            # ISP Name
            isp = data.get('isp', '?')
            return loc, isp
    except:
        pass
    return "Unknown", "Unknown"

def run(target):
    try:
        system_os = platform.system().lower()
        cmd = []
        tool_used = "Unknown"
        scan_mode = "Standard"

        # --- 🧹 INPUT CLEANING ---
        # Traceroute tools sirf domain lete hain (e.g., google.com), URL nahi (https://...)
        clean_target = target.replace("http://", "").replace("https://", "").split('/')[0]

        # --- 🛠️ SMART TOOL DETECTION & FIREWALL BYPASS LOGIC ---
        if system_os == 'windows':
            # Windows Standard
            cmd = ['tracert', '-h', '20', '-d', clean_target]
            tool_used = "tracert (ICMP)"
        else:
            # Linux: Priority 1 -> TCP Traceroute (Bypasses Firewalls using Port 443/80)
            if shutil.which("tcptraceroute"):
                # Port 443 (HTTPS) use karein taaki traffic legitimate lage
                cmd = ['tcptraceroute', '-n', '-m', '20', clean_target, '443']
                tool_used = "tcptraceroute (TCP/443)"
                scan_mode = "🔥 Firewall Bypass Mode"
            
            # Linux: Priority 2 -> Tracepath (Works well without Root)
            elif shutil.which("tracepath"):
                cmd = ['tracepath', '-n', '-m', '20', clean_target]
                tool_used = "tracepath (UDP)"
            
            # Linux: Priority 3 -> Standard Traceroute
            elif shutil.which("traceroute"):
                cmd = ['traceroute', '-n', '-m', '20', clean_target]
                tool_used = "traceroute (UDP)"
            
            else:
                return {
                    "ok": False, 
                    "error": "Error: No tracing tools found.\nSolution: Run 'sudo apt install tcptraceroute' in terminal."
                }

        # --- 📝 OUTPUT HEADER ---
        output_text = f"Starting ADVANCED TRACE on: {clean_target}\n"
        output_text += f"Tool: {tool_used} | Mode: {scan_mode}\n"
        output_text += "(Resolving path & location...)\n\n"
        
        # Table Header
        header = f"{'HOP':<4} | {'IP ADDRESS':<16} | {'LOCATION (City, CN)':<25} | {'ISP / ORGANIZATION'}"
        sep = "-" * len(header)
        output_text += f"{sep}\n{header}\n{sep}\n"

        # Execute Command
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Regex to find valid IPv4 addresses
        ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

        # Read Output Line by Line
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line: continue
            
            # --- PARSING LOGIC ---
            parts = line.split()
            hop_num = "?"
            
            # Hop Number Extraction (Handles multiple formats)
            if len(parts) > 0:
                if parts[0].isdigit():
                    hop_num = parts[0]
                elif len(parts) > 1 and parts[0] == ":" and parts[1].isdigit(): 
                    hop_num = parts[1]
                elif parts[0] == "1:":
                    hop_num = "1"

            # Check for Timeout / Blocked
            is_timeout = "*" in line or "no reply" in line.lower() or "Request timed out" in line

            # Find IP
            found_ips = ip_pattern.findall(line)
            
            if found_ips:
                # First match is usually the hop IP
                ip = found_ips[0]
                
                # Get Geo Data
                loc, isp = get_ip_location(ip)
                
                # Truncate long ISP names
                if len(isp) > 25: isp = isp[:22] + "..."
                
                # Print Row
                if hop_num.isdigit():
                    output_text += f"{hop_num:<4} | {ip:<16} | {loc:<25} | {isp}\n"
            
            elif is_timeout:
                # Agar timeout hai par hop number valid hai
                if hop_num.isdigit():
                    output_text += f"{hop_num:<4} | {'*':<16} | {'(Secure Node)':<25} | {'[Traffic Filtered]'}\n"

        output_text += sep + "\n"
        output_text += "[*] Trace Finished."

        return {"ok": True, "data": output_text}

    except Exception as e:
        return {"ok": False, "error": f"Execution Failed: {str(e)}"}    