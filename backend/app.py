import socket
import os
import sys
import json
import re # Added for cleaning
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import google.generativeai as genai

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
from tools import ping, traceroute, dns, whois, geoip, headers, links, subnet, nmap_safe, admin_finder, ssl_scanner, tech_detect
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
    if not raw_input: return ""
    target = raw_input.strip()
    if keep_protocol:
        if not target.startswith("http"): target = "http://" + target
        return target
    target = target.replace("https://", "").replace("http://", "")
    if "/" in target: target = target.split("/")[0]
    if ":" in target: target = target.split(":")[0]
    if target.startswith("www."): target = target[4:]
    return target

# --- 🗺️ TOOLS MAPPING ---
TOOLS = {
    'ping': ping, 'traceroute': traceroute, 'dns': dns,
    'whois': whois, 'geoip': geoip, 'headers': headers,
    'links': links, 'subnet': subnet, 'nmap': nmap_safe,
    'admin': admin_finder,
    'ssl': ssl_scanner,
    'tech': tech_detect
}

# --- 🧠 SMART MODEL DETECTOR ---
def get_best_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Priority Flash to avoid errors
        priorities = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        for p in priorities:
            if p in available_models: return p
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

    needs_full = (tool_name in ['links', 'headers', 'admin', 'tech'])
    target = get_clean_target(raw_target, keep_protocol=needs_full)
    
    try:
        result = TOOLS[tool_name].run(target)
        return jsonify(result)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Internal Error: {str(e)}"})

# --- 🤖 API: AI ANALYSIS (ANTI-CRASH VERSION) ---
@app.route('/api/analyze', methods=['POST'])
def analyze_result():
    data = request.json
    tool = data.get('tool')
    content = data.get('content')

    # 👇👇👇 YOUR API KEY 👇👇👇
    MY_API_KEY = "AIzaSyCdXaTo_y--LGAuEeQgPoSbat-Y8b1k6xg"
    # 👆👆👆👆👆👆👆👆👆👆👆👆👆

    if "YOUR_REAL_API_KEY" in MY_API_KEY:
        return jsonify({"ok": False, "error": "API Key Missing."})

    try:
        genai.configure(api_key=MY_API_KEY) 
        model_name = get_best_model()
        model = genai.GenerativeModel(model_name)

        # 🔥 PROMPT with JSON instructions
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
        ------------------------------------------------------------
        >>> Threat Score : [🟢 SAFE / 🟡 CAUTION / 🔴 CRITICAL]
        >>> Overview     : [Summary]

        [2] 🕵️ TECHNICAL VULNERABILITY DETECTED
        ------------------------------------------------------------
        >>> Finding : [Issue Name]
        >>> Details : [Details]

        [3] 💀 ATTACK SIMULATION (HACKER'S VIEW)
        ------------------------------------------------------------
        STEP 1: [Recon]
        STEP 2: [Exploit]
        STEP 3: [Damage]

        [4] 🛡️ STRATEGIC COUNTERMEASURES
        ------------------------------------------------------------
        01. [Fix 1]
        02. [Fix 2]

        RAW DATA:
        {content}
        """

        response = model.generate_content(prompt)
        clean_response = response.text.replace('```json', '').replace('```', '').strip()
        
        # 🔥 ANTI-CRASH LOGIC (THE FIX) 🔥
        try:
            # Step 1: Koshish karo JSON parse karne ki
            # strict=False helps ignore control characters
            result_json = json.loads(clean_response, strict=False)
        except Exception as e:
            # Step 2: Agar JSON fail hua (Invalid Control Character), to CRASH MAT HONA
            # Hum manually text ko wrap kar denge
            print(f"[AI RECOVERY] JSON Failed, using raw text fallback. Error: {e}")
            result_json = {
                "display_text": clean_response, 
                "speech_text": "Sir, analysis complete. Report screen par hai."
            }

        # Extra safety: Clean formatting just in case
        if "display_text" in result_json:
             result_json["display_text"] = result_json["display_text"].replace("**", "").replace("* ", "- ")

        return jsonify({"ok": True, "data": result_json})

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg: error_msg = "Model Not Found. Check API Key."
        return jsonify({"ok": False, "error": f"AI Error: {error_msg}"})

# --- 📄 PDF REPORT ---
@app.route('/api/report/single', methods=['POST'])
def single_report():
    data = request.json
    filename = f"Report_{data.get('tool')}_{datetime.now().strftime('%H%M%S')}.pdf"
    report_path = os.path.join(BACKEND_DIR, "report", filename)
    if not os.path.exists(os.path.dirname(report_path)): os.makedirs(os.path.dirname(report_path))
    if create_pdf(report_path, data.get('target'), data.get('tool'), data.get('content')):
        return send_file(report_path, as_attachment=True)
    return jsonify({"ok": False, "error": "PDF Failed"})

@app.route('/api/report/all', methods=['POST'])
def full_report():
    data = request.json
    target = get_clean_target(data.get('target'))
    content = ""
    tool_order = ['ping', 'geoip', 'ssl', 'tech', 'admin', 'dns', 'whois', 'headers', 'traceroute', 'nmap']
    
    for t in tool_order:
        content += f"\n{'='*40}\n TOOL: {t.upper()} \n{'='*40}\n"
        loop_target = "http://" + target if t in ['headers', 'tech', 'admin'] else target
        try:
            res = TOOLS[t].run(loop_target)
            content += res['data'] if res['ok'] else f"[FAIL] {res['error']}"
        except Exception as e: content += f"[ERROR] {e}"
        content += "\n\n"

    filename = f"FULL_RECON_{datetime.now().strftime('%H%M%S')}.pdf"
    report_path = os.path.join(BACKEND_DIR, "report", filename)
    if not os.path.exists(os.path.dirname(report_path)): os.makedirs(os.path.dirname(report_path))
    if create_pdf(report_path, target, "FULL SCAN", content, is_full_report=True):
        return send_file(report_path, as_attachment=True)
    return jsonify({"ok": False, "error": "PDF Failed"})

if __name__ == '__main__':
    print("🚀 SERVER STARTED: http://127.0.0.1:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')