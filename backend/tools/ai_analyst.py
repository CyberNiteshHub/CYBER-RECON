import google.generativeai as genai
import os

# --- 🔑 API KEY SECTION ---
API_KEY = "AIzaSyCdXaTo_y--LGAuEeQgPoSbat-Y8b1k6xg"

def analyze_data(scan_type, raw_data):
    # 1. Check API Key
    if "YAHAN_APNI" in API_KEY or not API_KEY:
        return {
            "ok": False, 
            "error": "API Key Missing! Please edit backend/tools/ai_analyst.py"
        }

    try:
        # 2. Configure Google AI
        genai.configure(api_key=API_KEY)
            
        # --- 🔥 SMART MODEL DETECTION ---
        active_model_name = ""
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if not available_models:
                return {"ok": False, "error": "API Key Valid but No Models found."}
                
            # Prefer fast models (Flash) for exhibition speed
            for m_name in available_models:
                if 'flash' in m_name:
                    active_model_name = m_name
                    break
            if not active_model_name:
                active_model_name = available_models[0]

        except Exception as e:
            return {"ok": False, "error": f"Failed to fetch model list: {str(e)}"}

        # 3. Initialize Model
        model = genai.GenerativeModel(active_model_name)

        # --- 🧠 EXHIBITION-READY PROMPT (HACKER MINDSET) ---
        prompt = f"""
        ROLE: Expert Cyber Security Consultant at a Science Exhibition.
        AUDIENCE: Judges and Students (Non-technical). They need to understand the RISK clearly.
        
        TASK: Analyze this '{scan_type}' scan result.
        
        RAW DATA:
        '''
        {raw_data[:4500]} 
        '''

        INSTRUCTIONS:
        1. NO asterisks (**), NO bold markdown. Use CAPITAL LETTERS for headers.
        2. Keep it SHORT, SCARY (where needed), but EDUCATIONAL.
        3. Follow this EXACT structure:

        [ SECURITY INTELLIGENCE REPORT ]

        [1] THREAT SCORE
        (Choose: 🟢 SAFE | 🟡 CAUTION | 🔴 CRITICAL)
        (One line explanation. E.g., "Safe. Only standard public ports are visible.")

        [2] WHAT DID WE FIND?
        (Simple explanation. E.g., "We found a Web Server (Port 80) and a Database (Port 3306).")
        (Use bullet points '•')

        [3] THE HACKER'S VIEW (⚠️)
        (Explain how a hacker would abuse this info. E.g., "A hacker sees Port 3306 open and will try to guess the Database password to steal data." or "With this IP location, a hacker knows exactly which city to target for social engineering.")

        [4] DEFENSE STRATEGY (🛡️)
        (How to fix it? E.g., "Close Port 3306 using a Firewall or use a VPN.")

        IMPORTANT:
        - If data is empty/failed, say "No usable intelligence found."
        - Focus on the "Hacker's View" to impress the judges.
        """

        # 5. Generate Content
        response = model.generate_content(prompt)
        
        # Clean up response (Remove accidental markdown)
        clean_text = response.text.replace("**", "").replace("##", "")
        
        return {"ok": True, "data": clean_text}

    except Exception as e:
        return {"ok": False, "error": f"AI Error: {str(e)}"}

# Test function
def run(target_data):
    return analyze_data("Test Scan", target_data)