import requests

def run(target):
    if not target.startswith("http"):
        target = "http://" + target
        
    output_text = f"[*] Detecting Technology Stack for: {target}\n\n"
    
    try:
        r = requests.get(target, timeout=5, verify=False)
        headers = r.headers
        
        # 1. Server Info
        if 'Server' in headers:
            output_text += f"🖥️ SERVER: {headers['Server']}\n"
        
        # 2. X-Powered-By (PHP, ASP.NET, etc)
        if 'X-Powered-By' in headers:
            output_text += f"⚡ POWERED BY: {headers['X-Powered-By']}\n"
            
        # 3. Cookies (Can reveal frameworks)
        if r.cookies:
            output_text += "🍪 COOKIES DETECTED:\n"
            for cookie in r.cookies:
                output_text += f"   - {cookie.name}\n"
        
        # 4. Content Checks (WordPress, React, etc)
        html = r.text.lower()
        detected = []
        
        if 'wp-content' in html: detected.append("WordPress")
        if 'react' in html: detected.append("React.js")
        if 'bootstrap' in html: detected.append("Bootstrap")
        if 'jquery' in html: detected.append("jQuery")
        if 'shopify' in html: detected.append("Shopify")
        
        if detected:
            output_text += f"\n🛠️ FRAMEWORKS/CMS DETECTED: {', '.join(detected)}\n"
        else:
            output_text += "\n[-] No specific CMS or Framework signatures found in HTML.\n"
            
        return {"ok": True, "data": output_text}

    except Exception as e:
        return {"ok": False, "error": str(e)}