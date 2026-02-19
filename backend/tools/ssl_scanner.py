import ssl
import socket
from datetime import datetime

def run(target):
    # Clean target
    hostname = target.replace("https://", "").replace("http://", "").split("/")[0]
    
    context = ssl.create_default_context()
    output_text = f"[*] Inspecting SSL Certificate for: {hostname}\n\n"
    
    try:
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Extract Info
                subject = dict(x[0] for x in cert['subject'])
                issuer = dict(x[0] for x in cert['issuer'])
                not_after = cert['notAfter']
                
                # Convert Date
                expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                days_left = (expiry_date - datetime.now()).days
                
                output_text += f"✅ ISSUED TO: {subject.get('commonName', 'Unknown')}\n"
                output_text += f"🏢 ISSUED BY: {issuer.get('commonName', 'Unknown')}\n"
                output_text += f"📅 EXPIRES ON: {not_after}\n"
                
                if days_left > 0:
                    output_text += f"⏳ DAYS LEFT: {days_left} days\n"
                else:
                    output_text += f"❌ EXPIRED: The certificate expired {abs(days_left)} days ago!\n"
                
                output_text += f"🔒 VERSION: {ssock.version()}\n"
                output_text += f"🔑 CIPHER: {ssock.cipher()[0]}\n"

        return {"ok": True, "data": output_text}

    except Exception as e:
        return {"ok": False, "error": f"SSL Handshake Failed. Target might use HTTP only.\nError: {e}"}