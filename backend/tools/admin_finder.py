import requests

def run(target):
    # Common admin paths
    paths = [
        'admin/', 'admin/login.php', 'administrator/', 'login/', 'wp-admin/', 
        'dashboard/', 'user/login', 'panel/', 'cpanel/', 'robots.txt'
    ]
    
    found = []
    
    # Target formatting
    if not target.startswith("http"):
        base_url = "http://" + target
    else:
        base_url = target
        
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    output_text = f"[*] Starting Admin Search on: {base_url}\n"
    output_text += "[*] Checking common paths... (This might take a few seconds)\n\n"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for path in paths:
            url = f"{base_url}/{path}"
            try:
                res = requests.get(url, headers=headers, timeout=3, allow_redirects=False)
                if res.status_code == 200:
                    output_text += f"[+] FOUND: {url} (Status: 200 OK)\n"
                    found.append(url)
                elif res.status_code == 302 or res.status_code == 301:
                    output_text += f"[!] REDIRECT: {url} (Possible Login)\n"
                    found.append(url)
            except:
                pass
        
        if not found:
            output_text += "[-] No common admin paths found.\n"
        else:
            output_text += f"\n[SUCCESS] Found {len(found)} hidden paths."
            
        return {"ok": True, "data": output_text}

    except Exception as e:
        return {"ok": False, "error": str(e)}