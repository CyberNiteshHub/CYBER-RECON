import dns.resolver

def run(target):
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        
        output_text = f"DNS Records Report for: {target}\n" + "="*60 + "\n"
        # Table Header
        output_text += f"{'TYPE':<6} | {'DATA / VALUE'}\n"
        output_text += "-"*60 + "\n"

        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        found_any = False

        for record_type in record_types:
            try:
                answers = resolver.resolve(target, record_type)
                found_any = True
                for rdata in answers:
                    # Format data nicely
                    data_str = rdata.to_text().replace('"', '') # Clean TXT records
                    if record_type == 'MX':
                         # Split MX preference and server
                         pref, server = data_str.split(' ', 1)
                         data_str = f"Pref: {pref}, Server: {server}"
                        
                    output_text += f"{record_type:<6} | {data_str}\n"
            except:
                continue # Record type not found, skip

        output_text += "-"*60 + "\n"
        
        if not found_any:
            return {"ok": False, "error": "No standard DNS records found."}
            
        return {"ok": True, "data": output_text}
    except Exception as e:
        return {"ok": False, "error": str(e)}