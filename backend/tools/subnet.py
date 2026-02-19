import ipaddress
import socket
import sys

def run(target):
    try:
        # --- 1. CLEAN INPUT ---
        target = target.strip()
        original_input = target
        
        # --- 2. INTELLIGENT RESOLUTION ---
        # Domain detection (e.g. google.com)
        if any(c.isalpha() for c in target) and "/" not in target:
            try:
                # Force IPv4 resolution
                resolved_ip = socket.gethostbyname(target)
                target = f"{resolved_ip}/24" # Default standard block
            except socket.gaierror:
                return {"ok": False, "error": f"Could not resolve domain: '{original_input}'. Check spelling or internet."}
        
        # Plain IP detection (e.g. 192.168.1.1 -> /24)
        elif "/" not in target:
            target += "/24"

        # --- 3. CORE CALCULATION ---
        try:
            net = ipaddress.IPv4Network(target, strict=False)
        except ipaddress.AddressValueError:
             return {"ok": False, "error": "Invalid IP Address format."}
        except ipaddress.NetmaskValueError:
             return {"ok": False, "error": "Invalid CIDR/Netmask."}

        # --- 4. ADVANCED METRICS ---
        
        # A. IP Classification
        ip_type = "Public (Internet Routable)"
        if net.is_private: ip_type = "Private (Local Network / RFC 1918)"
        elif net.is_loopback: ip_type = "Loopback (Localhost)"
        elif net.is_link_local: ip_type = "Link-Local (APIPA)"
        elif net.is_multicast: ip_type = "Multicast"
        elif net.is_reserved: ip_type = "Reserved (IETF)"

        # B. Class Detection
        first_octet = int(str(net.network_address).split('.')[0])
        ip_class = "Unknown"
        if 1 <= first_octet <= 126: ip_class = "Class A (Large Network)"
        elif 128 <= first_octet <= 191: ip_class = "Class B (Medium Network)"
        elif 192 <= first_octet <= 223: ip_class = "Class C (Small Network)"
        
        # C. Hexadecimal Representation
        hex_ip = '.'.join([f"{int(x):02X}" for x in str(net.network_address).split('.')])
        hex_mask = '.'.join([f"{int(x):02X}" for x in str(net.netmask).split('.')])

        # D. Binary Visualization (Visual Split)
        # Convert IP to 32-bit binary string
        # 192.168.1.0 -> 11000000.10101000.00000001.00000000
        binary_octets = [bin(int(x))[2:].zfill(8) for x in str(net.network_address).split('.')]
        full_binary = "".join(binary_octets)
        
        # Insert divider at CIDR position
        prefix_len = net.prefixlen
        net_bits = full_binary[:prefix_len]
        host_bits = full_binary[prefix_len:]
        
        # Re-format for display (with colors logic handled by frontend, here purely text)
        visual_binary = f"{net_bits} | {host_bits}"
        
        # E. Reverse DNS Pointer
        # Useful for PTR record lookups
        rev_dns = net.network_address.reverse_pointer

        # --- 5. GENERATE PRO REPORT ---
        output = f"""
╔{'═'*65}╗
║  ADVANCED SUBNET ANALYZER                    ║
╠{'═'*65}╣
║  INPUT    : {original_input:<48} ║
║  CALC     : {str(net):<48} ║
╚{'═'*65}╝

┌──[ NETWORK IDENTITY ]{'─'*47}
│  IP Type           : {ip_type}
│  Network Class     : {ip_class}
│  Reverse DNS (PTR) : {rev_dns}
└{'─'*67}

┌──[ ADDRESS BLOCKS ]{'─'*49}
│  Network Address   : {str(net.network_address)}
│  Broadcast Address : {str(net.broadcast_address)}
│  Netmask           : {str(net.netmask)}
│  Wildcard Mask     : {str(net.hostmask)}
└{'─'*67}

┌──[ CAPACITY PLANNING ]{'─'*48}
│  CIDR Notation     : /{net.prefixlen}
│  Total IP Addresses: {net.num_addresses:,}
│  Usable Hosts      : {net.num_addresses - 2 if net.num_addresses > 2 else 0:,}
│  Host Range        : {list(net.hosts())[0]} <---> {list(net.hosts())[-1]}
└{'─'*67}

┌──[ ENGINEER DATA ]{'─'*50}
│  Hex Network       : {hex_ip}
│  Hex Netmask       : {hex_mask}
│  Binary Structure  : (Network Bits | Host Bits)
│  {visual_binary}
└{'─'*67}
"""
        return {"ok": True, "data": output}

    except Exception as e:
        return {"ok": False, "error": f"Calculation Error: {str(e)}"}   