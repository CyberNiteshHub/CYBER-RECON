import socket
import re
import datetime

def get_raw_whois(server, target):
    """
    Helper function to perform the raw socket connection.
    """
    try:
        # IPv4 Patch app.py me hai, yahan normal socket use karenge
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((server, 43))
        s.send(f"{target}\r\n".encode())
        
        response = b""
        while True:
            data = s.recv(4096)
            if not data: break
            response += data
        s.close()
        return response.decode(errors='ignore')
    except Exception as e:
        return f"Error: {str(e)}"

def extract_field(pattern, text):
    """
    Regex se specific data nikalne ke liye helper function.
    """
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def run(target):
    try:
        # --- 1. CLEAN INPUT ---
        clean_target = target.replace("http://", "").replace("https://", "").replace("www.", "")
        if "/" in clean_target: clean_target = clean_target.split('/')[0]
        if ":" in clean_target: clean_target = clean_target.split(':')[0]

        # --- 2. INTELLIGENT QUERY (IANA -> REGISTRAR) ---
        # Step A: Ask IANA (Root) who manages this domain?
        iana_data = get_raw_whois("whois.iana.org", clean_target)
        
        # Referral server dhundo
        referral_server = extract_field(r"refer:\s*(.+)", iana_data)
        
        final_data = iana_data
        used_server = "whois.iana.org"

        # Step B: Agar Referral server mila (jaise whois.verisign-grs.com), to wahan se poocho
        if referral_server:
            # Referral server aksar port 43 pe hota hai
            registrar_data = get_raw_whois(referral_server, clean_target)
            if "Error:" not in registrar_data:
                final_data = registrar_data
                used_server = referral_server
            
            # Kuch TLDs (like .com) ka double referral hota hai. 
            # Check if there is ANOTHER referral inside the registrar data
            secondary_referral = extract_field(r"Registrar WHOIS Server:\s*(.+)", final_data)
            if secondary_referral and secondary_referral != referral_server:
                deep_data = get_raw_whois(secondary_referral, clean_target)
                if "Error:" not in deep_data:
                    final_data = deep_data
                    used_server = secondary_referral

        # --- 3. PARSING & EXTRACTION (The Pro Part) ---
        # Ab hum raw text me se moti-moti kaam ki cheezein nikalenge
        
        domain_name = extract_field(r"Domain Name:\s*(.+)", final_data) or clean_target
        registrar = extract_field(r"Registrar:\s*(.+)", final_data) or "Unknown"
        created_date = extract_field(r"Creation Date:\s*(.+)", final_data)
        expiry_date = extract_field(r"Registry Expiry Date:\s*(.+)", final_data) or extract_field(r"Expiry Date:\s*(.+)", final_data)
        updated_date = extract_field(r"Updated Date:\s*(.+)", final_data)
        
        # Name Servers (List nikalna)
        ns_matches = re.findall(r"Name Server:\s*(.+)", final_data, re.IGNORECASE)
        name_servers = list(set(ns_matches)) # Remove duplicates
        
        # Abuse Contact (Security ke liye sabse zaruri)
        abuse_email = extract_field(r"Registrar Abuse Contact Email:\s*(.+)", final_data)
        abuse_phone = extract_field(r"Registrar Abuse Contact Phone:\s*(.+)", final_data)

        # Domain Status (Active/Locked)
        status_matches = re.findall(r"Domain Status:\s*(\S+)", final_data)
        # Clean status (remove URLs)
        clean_status = [s.split(' ')[0] for s in status_matches if "http" not in s]
        if not clean_status: clean_status = ["Active"]

        # --- 4. PRIVACY CHECK & FORMATTING ---
        # Check karte hain ki kya data redacted hai?
        privacy_active = False
        if "REDACTED" in final_data or "Privacy" in final_data or "GDPR" in final_data:
            privacy_active = True

        # Date Cleaning (ISO format ko readable banana)
        def clean_date(d):
            if d: return d.replace("T", " ").replace("Z", "")
            return "N/A"

        # --- 5. GENERATE PRO REPORT ---
        scan_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        output = f"""
╔{'═'*70}╗
║  DOMAIN INTELLIGENCE REPORT (WHOIS)         |  {scan_time:<19} ║
╠{'═'*70}╣
║  TARGET     : {clean_target:<53}  ║
║  REGISTRAR  : {registrar[:53]:<53}  ║
╚{'═'*70}╝

┌──[ VITAL STATISTICS ]{'─'*52}
│  Creation Date  : {clean_date(created_date)}
│  Last Updated   : {clean_date(updated_date)}
│  Expiration     : {clean_date(expiry_date)}  <-- (Check Validity)
│  Database Srvr  : {used_server}
└{'─'*74}

┌──[ INFRASTRUCTURE (Name Servers) ]{'─'*39}
"""
        if name_servers:
            for ns in name_servers[:4]: # Top 4 NS only
                output += f"│  ➤ {ns.lower()}\n"
        else:
            output += "│  [!] No Name Servers Found.\n"
        output += f"└{'─'*74}\n"

        output += f"\n┌──[ SECURITY & OWNERSHIP ]{'─'*48}\n"
        if privacy_active:
            output += f"│  Owner Name     : 🔒 PRIVACY PROTECTED (GDPR Compliant)\n"
            output += f"│  Organization   : 🔒 REDACTED FOR PRIVACY\n"
        else:
            # Agar privacy nahi hai (kismat se), to raw data check karna padega
            output += f"│  Owner Name     : (See Raw Data below)\n"
        
        output += f"│  Domain Status  : {', '.join(clean_status[:3])}\n"
        output += f"│  Abuse Email    : {abuse_email if abuse_email else 'N/A'}\n"
        output += f"│  Abuse Phone    : {abuse_phone if abuse_phone else 'N/A'}\n"
        output += f"└{'─'*74}\n"

        output += "\n" + "="*74 + "\n"
        output += "[ RAW DATA APPENDIX - FULL SERVER RESPONSE ]\n"
        output += "="*74 + "\n"
        output += final_data.strip()

        return {"ok": True, "data": output}

    except Exception as e:
        return {"ok": False, "error": f"Whois Lookup Failed: {str(e)}"}