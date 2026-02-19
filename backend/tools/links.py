import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# SSL Warning ko chupane ke liye
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run(target):
    try:
        # --- 1. SETUP ROBUST SESSION ---
        session = requests.Session()
        # Retry logic: Agar fail ho to 3 baar koshish karega
        retries = Retry(
            total=3, 
            backoff_factor=0.5, 
            status_forcelist=[500, 502, 503, 504],
            redirect=10 # Redirect limit taaki loop na bane
        )
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        # --- 2. URL CLEANUP ---
        if not target.startswith("http"):
            target = "http://" + target
            
        # --- 3. SEND REQUEST (Standard Mode) ---
        # Note: Hum ab manual IP replace nahi kar rahe.
        # Backend ka Global Patch (app.py) apne aap IPv4 handle kar lega.
        headers_ua = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Request bhejo (verify=False taaki SSL error na roke)
        response = session.get(target, headers=headers_ua, timeout=15, verify=False)
        
        # --- 4. PARSE HTML ---
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Junk links (javascript, mailto, etc.) ko hatao
            if href.startswith(('javascript:', 'mailto:', '#', 'tel:')): 
                continue
                
            # Relative URL ko Full URL banao (e.g., /about -> https://site.com/about)
            full_link = urljoin(response.url, href) 
            links.append(full_link)
            
        unique_links = sorted(list(set(links)))
        count = len(unique_links)
        
        # --- 5. GENERATE REPORT ---
        domain = target.replace("http://", "").replace("https://", "").split("/")[0]
        
        output = f"╔{'═'*60}╗\n"
        output += f"║  PAGE LINK EXTRACTOR REPORT                ║\n"
        output += f"╠{'═'*60}╣\n"
        output += f"║  TARGET : {domain:<40} ║\n"
        output += f"║  FOUND  : {count:<40} ║\n"
        output += f"╚{'═'*60}╝\n\n"
        
        output += f"[*] Extraction Successful.\n"
        output += f"[*] Top 200 Links Found:\n\n"

        for i, link in enumerate(unique_links[:200], 1):
            output += f"[{i:03}] {link}\n"
            
        if count > 200:
            output += f"\n...and {count - 200} more links hidden."

        return {"ok": True, "data": output}

    except Exception as e:
        # Error handling
        error_msg = str(e)
        if "Exceeded 30 redirects" in error_msg:
            return {"ok": False, "error": "Target Redirect Loop Detected. Try using the exact URL (e.g., https://www.google.com)."}
        
        return {"ok": False, "error": f"Link Extraction Failed: {error_msg}"}