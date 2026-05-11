import socket
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
import traceback

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    if _env_path.is_file():
        load_dotenv(_env_path)
except ImportError:
    pass

# --- 🌐 FIREBASE INTEGRATION ---
FIREBASE_ENABLED = False
firebase_db = None

try:
    from firebase_db_simple_rest_api import firebase_db
    FIREBASE_ENABLED = bool(getattr(firebase_db, "initialized", False))
    if FIREBASE_ENABLED:
        print("[✓✓✓] Firebase integration LOADED and READY!")
    else:
        print("[!] Firebase module loaded but persistence disabled (set FIREBASE_DATABASE_URL).")
except ImportError as e:
    print(f"[!] Firebase not available: {e}")
    FIREBASE_ENABLED = False

# --- 🔥 GLOBAL IPv4 FORCE PATCH ---
try:
    old_getaddrinfo = socket.getaddrinfo    
    def new_getaddrinfo(*args, **kwargs):
        host = args[0]
        if host in ['localhost', '127.0.0.1', '0.0.0.0']:
            responses = old_getaddrinfo(*args, **kwargs)
            return [r for r in responses if r[0] == socket.AF_INET]
        return old_getaddrinfo(*args, **kwargs)
    socket.getaddrinfo = new_getaddrinfo
except Exception:
    pass

# --- 🛠️ IMPORT TOOLS ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools import ping, traceroute, dns, whois, geoip, headers, links, subnet, nmap_safe, admin_finder, ssl_scanner, tech_detect, sqli
from report.pdf_generator import create_pdf

# --- 📂 PATH SYSTEM ---
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))  
PROJECT_DIR = os.path.dirname(BACKEND_DIR)                
FRONTEND_DIR = os.path.join(PROJECT_DIR, 'frontend')      

if not os.path.exists(FRONTEND_DIR):
    print(f"[CRITICAL] Frontend not found at: {FRONTEND_DIR}")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

# --- 🛡️ INPUT CLEANING ---
def get_clean_target(raw_input, keep_protocol=False):
    if not raw_input: 
        return ""
    target = raw_input.strip()
    if keep_protocol:
        if not target.startswith("http"): 
            target = "http://" + target
        return target
    target = target.replace("https://", "").replace("http://", "")
    if "/" in target: 
        target = target.split("/")[0]
    if ":" in target: 
        target = target.split(":")[0]
    if target.startswith("www."): 
        target = target[4:]
    return target

# --- 🗺️ TOOLS MAPPING ---
TOOLS = {
    'ping': ping, 'traceroute': traceroute, 'dns': dns,
    'whois': whois, 'geoip': geoip, 'headers': headers,
    'links': links, 'subnet': subnet, 'nmap': nmap_safe,
    'admin': admin_finder,
    'ssl': ssl_scanner,
    'tech': tech_detect,
    'sqli': sqli
}

# --- 🧠 SMART MODEL DETECTOR ---
def get_best_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        priorities = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        for p in priorities:
            if p in available_models: 
                return p
        return available_models[0] if available_models else 'gemini-1.5-flash'
    except:
        return 'gemini-1.5-flash'

# --- 🏠 HOME ROUTE ---
@app.route('/')
def index():
    return send_file(os.path.join(FRONTEND_DIR, "index.html"))

# --- 🚀 API: RUN TOOL ---
@app.route('/api/run', methods=['GET'])
def run_tool():
    raw_target = request.args.get('target')
    tool_name = request.args.get('tool')
    
    if not raw_target or not tool_name:
        return jsonify({"ok": False, "error": "Target Required"})
    
    if tool_name not in TOOLS:
        return jsonify({"ok": False, "error": "Invalid Tool"})

    needs_full = (tool_name in ['links', 'headers', 'admin', 'tech', 'sqli'])
    target = get_clean_target(raw_target, keep_protocol=needs_full)
    
    try:
        result = TOOLS[tool_name].run(target)
        
        # --- 🌐 FIREBASE AUTO-SAVE (FIXED) ---
        if FIREBASE_ENABLED and result.get('ok') and firebase_db:
            try:
                result_text = result.get('data', '')
                vuln_count = result_text.count('🔴') + result_text.count('🟡') + result_text.count('🟢')
                severity_high = result_text.count('🔴')
                severity_medium = result_text.count('🟡')
                severity_low = result_text.count('🟢')
                
                firebase_db.save_scan_result(
                    target=target,
                    tool=tool_name,
                    result_data=result_text,
                    vulnerable_count=vuln_count,
                    severity_high=severity_high,
                    severity_medium=severity_medium,
                    severity_low=severity_low
                )
                print(f"[✓] Saved to Firebase: {tool_name} - {target}")
            except Exception as e:
                print(f"[!] Firebase save error: {e}")
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Internal Error: {str(e)}"})

# --- 🔐 API: SQL INJECTION SCAN ---
@app.route('/api/sqli', methods=['POST'])
def sql_injection_scan():
    try:
        data = request.json or {}
        target_url = data.get('target', '')
        
        if not target_url:
            return jsonify({"ok": False, "error": "Target URL Required"})
        
        if not target_url.startswith("http"):
            target_url = "http://" + target_url
        
        result = sqli.run(target_url)
        
        # --- 🌐 FIREBASE AUTO-SAVE FOR SQL INJECTION ---
        if FIREBASE_ENABLED and result.get('ok') and firebase_db:
            try:
                firebase_db.save_scan_result(
                    target=target_url,
                    tool='sqli',
                    result_data=result.get('data', ''),
                    vulnerable_count=result.get('techniques', 0),
                    severity_high=1 if result.get('vulnerable') else 0,
                    severity_medium=0,
                    severity_low=0
                )
                print(f"[✓] SQL Injection saved to Firebase: {target_url}")
            except Exception as e:
                print(f"[!] Firebase SQL save error: {e}")
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"ok": False, "error": f"SQL Injection Error: {str(e)}"})

# --- 🤖 API: AI ANALYSIS ---
@app.route('/api/analyze', methods=['POST'])
def analyze_result():
    try:
        data = request.json or {}
        tool = data.get('tool', 'unknown')
        content = data.get('content', '')

        MY_API_KEY = (os.environ.get("GEMINI_API_KEY") or "").strip()
        bad = {"", "your api key", "your_api_key", "your-api-key-here", "your_api_key_here"}
        if not MY_API_KEY or MY_API_KEY.lower() in bad:
            return jsonify({
                "ok": False,
                "error": "Set GEMINI_API_KEY in a .env file or your environment (see env.example).",
            })

        genai.configure(api_key=MY_API_KEY) 
        model_name = get_best_model()
        model = genai.GenerativeModel(model_name)

        prompt = f"""
        ROLE: Expert Cyber Security Auditor (Cortex AI).
        TASK: Analyze this '{tool}' scan result.
        
        FORMATTING:
        - Use UPPERCASE for section headers.
        - NO MARKDOWN bold (**).
        - IMPORTANT: Return valid JSON. Avoid unescaped newlines inside strings.

        OUTPUT JSON STRUCTURE:
        {{
            "display_text": "Your Full Hacker Style Report Here...",
            "speech_text": "Short Hindi explanation script..."
        }}
        
        REPORT DESIGN (Put this inside display_text):
        ============================================================
        ⚡ CLASSIFIED SECURITY INTELLIGENCE REPORT // ID: {tool.upper()}
        ============================================================

        [1] 📊 EXECUTIVE THREAT ASSESSMENT
        [2] 🕵️ TECHNICAL VULNERABILITY DETECTED
        [3] 💀 ATTACK SIMULATION (HACKER'S VIEW)
        [4] 🛡️ STRATEGIC COUNTERMEASURES

        RAW DATA:
        {content}
        """

        response = model.generate_content(prompt)
        clean_response = response.text.replace('```json', '').replace('```', '').strip()
        
        try:
            result_json = json.loads(clean_response, strict=False)
        except:
            result_json = {
                "display_text": clean_response, 
                "speech_text": "Analysis complete. Report ready."
            }

        if "display_text" in result_json:
            result_json["display_text"] = result_json["display_text"].replace("**", "").replace("* ", "- ")

        return jsonify({"ok": True, "data": result_json})

    except Exception as e:
        return jsonify({"ok": False, "error": f"AI Error: {str(e)}"})

# --- 📊 API: DASHBOARD STATS ---
@app.route('/api/dashboard', methods=['GET'])
def dashboard_stats():
    try:
        if FIREBASE_ENABLED and firebase_db:
            stats = firebase_db.get_statistics()
            recent_scans = firebase_db.get_recent_scans(limit=10)
            
            return jsonify({
                "ok": True,
                "stats": stats,
                "recent_scans": recent_scans
            })
        else:
            return jsonify({
                "ok": False,
                "error": "Firebase not available"
            })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# --- 📄 PDF REPORT ---
@app.route('/api/report/single', methods=['POST'])
def single_report():
    try:
        data = request.json or {}
        filename = f"Report_{data.get('tool')}_{datetime.now().strftime('%H%M%S')}.pdf"
        report_path = os.path.join(BACKEND_DIR, "report", filename)
        if not os.path.exists(os.path.dirname(report_path)): 
            os.makedirs(os.path.dirname(report_path))
        if create_pdf(report_path, data.get('target'), data.get('tool'), data.get('content')):
            return send_file(report_path, as_attachment=True)
        return jsonify({"ok": False, "error": "PDF Failed"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route('/api/report/all', methods=['POST'])
def full_report():
    try:
        data = request.json or {}
        target = get_clean_target(data.get('target', ''))
        content = ""
        tool_order = ['ping', 'geoip', 'ssl', 'tech', 'admin', 'dns', 'whois', 'headers', 'traceroute', 'nmap']
        
        for t in tool_order:
            content += f"\n{'='*40}\n TOOL: {t.upper()} \n{'='*40}\n"
            loop_target = "http://" + target if t in ['headers', 'tech', 'admin'] else target
            try:
                res = TOOLS[t].run(loop_target)
                content += res['data'] if res['ok'] else f"[FAIL] {res['error']}"
            except Exception as e: 
                content += f"[ERROR] {e}"
            content += "\n\n"

        filename = f"FULL_RECON_{datetime.now().strftime('%H%M%S')}.pdf"
        report_path = os.path.join(BACKEND_DIR, "report", filename)
        if not os.path.exists(os.path.dirname(report_path)): 
            os.makedirs(os.path.dirname(report_path))
        if create_pdf(report_path, target, "FULL SCAN", content, is_full_report=True):
            return send_file(report_path, as_attachment=True)
        return jsonify({"ok": False, "error": "PDF Failed"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

if __name__ == '__main__':
    print("\n")
    print("="*60)
    print("🚀 CYBER RECON TOOLKIT - STARTING SERVER")
    print("="*60)
    print(f"[✓] Firebase Status: {'ENABLED ✅' if FIREBASE_ENABLED else 'DISABLED ❌'}")
    print(f"[✓] Frontend Path: {FRONTEND_DIR}")
    print(f"[✓] Backend Path: {BACKEND_DIR}")
    print(f"[✓] URL: http://127.0.0.1:5000")
    print(f"[✓] Dashboard: http://127.0.0.1:5000/dashboard.html")
    print("="*60)
    print("\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')