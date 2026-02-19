import requests
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def run(target):
    try:
        # --- 1. SETUP SESSION ---
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # --- 2. CLEAN TARGET ---
        # "https://google.com/path" -> "google.com"
        clean_target = target.replace("http://", "").replace("https://", "").split('/')[0]

        # --- 3. FORCE IPv4 RESOLUTION (The Fix) ---
        # Step A: Resolve Target to IP
        try:
            target_ip = socket.gethostbyname(clean_target)
        except:
            target_ip = clean_target # Fallback to original if DNS fails

        # Step B: Resolve API Host (ip-api.com) to IP
        api_host = "ip-api.com"
        try:
            api_ip = socket.gethostbyname(api_host)
            # URL me IP use karenge taaki IPv6 ki wajah se block na ho
            url = f"http://{api_ip}/json/{target_ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
            # Host header zaroori hai
            headers_ua = {
                'Host': api_host,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CyberRecon-Tool/3.5'
            }
        except:
            # Fallback normal URL
            url = f"http://ip-api.com/json/{target_ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
            headers_ua = {'User-Agent': 'CyberRecon/3.5'}

        # --- 4. FETCH GEO DATA ---
        response = session.get(url, headers=headers_ua, timeout=10)
        data = response.json()
        
        if data['status'] == 'fail':
            return {"ok": False, "error": f"GeoIP Failed: {data.get('message')}"}

        lat = data.get('lat')
        lon = data.get('lon')

        # --- 5. REVERSE GEOCODING (Address Detail) ---
        address_display = "Scanning detailed address..."
        try:
            # Nominatim (OpenStreetMap)
            # Isko hum IP se call nahi karenge kyunki SSL error aa sakta hai
            # Par try-except block hume bacha lega agar fail hua
            geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
            geo_headers = {'User-Agent': 'CyberRecon-Tool/1.0'} # Custom UA required by OSM
            
            geo_resp = requests.get(geo_url, headers=geo_headers, timeout=5)
            
            if geo_resp.status_code == 200:
                geo_data = geo_resp.json()
                address_display = geo_data.get('display_name', 'Detailed address not found')
            else:
                address_display = f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
        except:
            # Silent fallback
            address_display = f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"

        # --- 6. MAP LINKS ---
        # Google Maps link with Satellite view parameter
        maps_link = f"http://maps.google.com/maps?q={lat},{lon}&ll={lat},{lon}&t=k"

        # --- 7. GENERATE ASCII REPORT ---
        output = f"""
+-----------------------+-----------------------------------------+
| FIELD                 | VALUE                                   |
+-----------------------+-----------------------------------------+
| Target IP             | {str(data.get('query', 'N/A')):<39} |
| Organization          | {str(data.get('org', 'N/A'))[:39]:<39} |
| ISP                   | {str(data.get('isp', 'N/A'))[:39]:<39} |
| ASN                   | {str(data.get('as', 'N/A'))[:39]:<39} |
+-----------------------+-----------------------------------------+
| Country               | {str(data.get('country', 'N/A')):<39} |
| Region / State        | {str(data.get('regionName', 'N/A')):<39} |
| City                  | {str(data.get('city', 'N/A')):<39} |
| ZIP Code              | {str(data.get('zip', 'N/A')):<39} |
| Timezone              | {str(data.get('timezone', 'N/A')):<39} |
+-----------------------+-----------------------------------------+
| Latitude / Longitude  | {str(lat) + " / " + str(lon):<39} |
+-----------------------+-----------------------------------------+
"""
        return {
            "ok": True, 
            "data": output, 
            "meta": {
                "lat": lat,
                "lon": lon,
                "address": address_display,
                "map_link": maps_link
            }
        }

    except Exception as e:
        return {"ok": False, "error": f"GeoIP Connection Error: {str(e)}"}