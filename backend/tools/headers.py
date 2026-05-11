import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
from urllib.parse import urlparse

# SSL Warnings hide (Clean Output)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run(target):
    try:
        # --- 1. SETUP SESSION ---
        session = requests.Session()
        # Retry Logic: Agar fail ho to 3 baar try karega
        retries = Retry(
            total=3, 
            backoff_factor=0.5, 
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        # --- 2. URL CLEANUP ---
        if not target.startswith("http"):
            target = "http://" + target

        # Domain name nikal rahe hain report ke liye
        parsed = urlparse(target)
        hostname = parsed.netloc

        # --- 3. SEND REQUEST (Standard Mode) ---
        # Note: Hum ab manual IP replace nahi kar rahe.
        # App.py ka Global Patch apne aap IPv4 handle kar lega.
        # Isse Redirect Loop (30 redirects error) nahi aayega.
        
        headers_ua = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # verify=False rakha hai taaki SSL errors ignore ho sakein
        response = session.get(target, headers=headers_ua, timeout=10, verify=False, allow_redirects=True)

        # --- 4. FORMAT OUTPUT ---
        output_text = ""
        output_text += f"╔{'═'*60}╗\n"
        output_text += f"║  HTTP SERVER HEADERS ANALYSIS              ║\n"
        output_text += f"╠{'═'*60}╣\n"
        output_text += f"║  TARGET : {hostname:<40} ║\n"
        output_text += f"║  STATUS : {response.status_code} {response.reason:<36} ║\n"
        output_text += f"╚{'═'*60}╝\n\n"

        output_text += f"┌──[ RAW HEADERS ]{'─'*47}\n"
        
        for key, value in response.headers.items():
            # Agar value bahut lambi hai to truncate karo taaki UI na fategi
            if len(value) > 80: value = value[:77] + "..."
            output_text += f"│  {key:<25} : {value}\n"
            
        output_text += f"└{'─'*65}\n"

        # --- 5. SECURITY CHECK ---
        security_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-XSS-Protection',
            'X-Content-Type-Options'
        ]

        missing_headers = [h for h in security_headers if h not in response.headers]
        
        output_text += "\n"
        if missing_headers:
            output_text += f"┌──[ SECURITY RISK ANALYSIS ]{'─'*39}\n"
            for m in missing_headers:
                 output_text += f"│  [-] Missing Header : {m}\n"
            output_text += f"└{'─'*65}\n"
        else:
            output_text += "[+] EXCELLENT: All major security headers are present.\n"

        return {"ok": True, "data": output_text}

    except Exception as e:
        # Error ko saaf dikhana
        error_msg = str(e)
        if "Exceeded 30 redirects" in error_msg:
            return {"ok": False, "error": "Target Redirect Loop Detected. Try using the exact URL (e.g., https://www.google.com)."}
        
        return {"ok": False, "error": f"Header Fetch Failed: {error_msg}"}