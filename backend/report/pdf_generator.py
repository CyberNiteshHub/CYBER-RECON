from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
import os
import textwrap

# --- 🎨 COLOR PALETTE (Cyber Theme) ---
THEME_DARK = HexColor('#0F172A')       # Dark Navy (Header)
THEME_ACCENT = HexColor('#00FF41')     # Hacker Green
THEME_CYAN = HexColor('#00F0FF')       # Cyber Cyan
THEME_RED = HexColor('#FF0055')        # Alert Red
THEME_GRAY_BG = HexColor('#F3F4F6')    # Light Gray for Terminal Box
TEXT_DARK = HexColor('#000000')        # PITCH BLACK (Readable)
TEXT_LIGHT = HexColor('#FFFFFF')       # White Text
TEXT_GRAY = HexColor('#64748B')        # Footer Gray

def sanitize_text_for_pdf(text):
    """
    FIX: Replaces unsupported fancy border characters with 
    hacker-style ASCII characters to prevent '????' in PDF.
    """
    replacements = {
        # Box Drawing Characters -> ASCII
        '═': '=', '─': '-', '│': '|', '║': '|',
        '╔': '+', '╗': '+', '╚': '+', '╝': '+',
        '╠': '+', '╣': '+', '╤': '+', '╧': '+',
        '╟': '+', '╢': '+', '┼': '+', '╋': '+',
        '┌': '+', '┐': '+', '└': '+', '┘': '+',
        '╭': '+', '╮': '+', '╰': '+', '╯': '+',
        
        # Icons -> Text equivalents
        '✔': '[OK]', '✓': '[OK]', 
        '✖': '[X]', '✗': '[X]',
        '⚠': '[!]', '⚡': '[*]',
        '➤': '>>', '●': '*', '•': '-',
        '▶': '>', '◀': '<'
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Remove any other non-printable unicode chars just in case
    return text.encode('latin-1', 'replace').decode('latin-1')

def draw_header(c, width, height, target, tool_name):
    """Draws the Pro Header (Isolated State)"""
    c.saveState()
    
    # 1. Background
    c.setFillColor(THEME_DARK)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    # 2. Title
    c.setFillColor(TEXT_LIGHT)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 45, "CYBER RECON")
    
    c.setFillColor(THEME_ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, height - 60, "ADVANCED INTELLIGENCE TOOLKIT v1.0")

    # 3. Info
    c.setFillColor(TEXT_LIGHT)
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 40, height - 35, f"TARGET: {target}")
    c.drawRightString(width - 40, height - 50, f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawRightString(width - 40, height - 65, f"MODULE: {tool_name.upper()}")

    # 4. Confidential
    c.setStrokeColor(THEME_RED)
    c.setLineWidth(2)
    c.roundRect(width - 160, height - 90, 120, 20, 4, stroke=True, fill=False)
    c.setFillColor(THEME_RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width - 100, height - 84, "CONFIDENTIAL")

    # 5. Line
    c.setStrokeColor(THEME_CYAN)
    c.setLineWidth(3)
    c.line(0, height - 100, width, height - 100)
    
    c.restoreState()

def draw_footer(c, width, height, page_num):
    """Draws the Footer (Isolated State)"""
    c.saveState()
    
    c.setFillColor(TEXT_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(40, 30, "© 2026 Project Cyber Recon | Dept. of BCA, BLJS College Tosham. All Rights Reserved.")
    c.drawRightString(width - 40, 30, f"Page {page_num}")
    
    c.setStrokeColor(THEME_DARK)
    c.setLineWidth(1)
    c.line(40, 45, width - 40, 45)
    
    c.restoreState()

def draw_watermark(c, width, height):
    c.saveState()
    c.translate(width/2, height/2)
    c.rotate(45)
    c.setFillColor(HexColor('#E5E7EB')) 
    c.setFont("Helvetica-Bold", 80)
    c.drawCentredString(0, 0, "CYBER RECON")
    c.restoreState()

def create_pdf(filename, target, tool_name, content, is_full_report=False):
    try:
        report_dir = os.path.dirname(filename)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        page_num = 1
        
        # Setup Page 1
        draw_header(c, width, height, target, tool_name)
        draw_footer(c, width, height, page_num)
        draw_watermark(c, width, height)
        
        # Executive Summary Box
        c.saveState()
        c.setFillColor(THEME_GRAY_BG)
        c.roundRect(40, height - 180, width - 80, 60, 6, fill=True, stroke=False)
        
        c.setFillColor(THEME_DARK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(55, height - 145, "EXECUTIVE SUMMARY")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor('#059669')) # Green
        c.drawString(55, height - 165, "[OK] Target Online")
        c.drawString(200, height - 165, "[OK] Scan Completed")
        
        if is_full_report:
             c.setFillColor(THEME_RED)
             c.drawString(400, height - 165, "[!] Full Vulnerability Scan")
        else:
             c.setFillColor(HexColor('#0284C7')) # Blue
             c.drawString(400, height - 165, "[i] Single Module Analysis")
        c.restoreState()

        # Content Setup
        c.setFillColor(THEME_DARK)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 210, f"01 // SCAN RESULTS: {tool_name.upper()}")
        
        text_y = height - 240
        line_height = 12
        bottom_margin = 60
        
        c.setFont("Courier", 9)
        c.setFillColor(TEXT_DARK)

        # 🔥 SANITIZE CONTENT BEFORE PRINTING
        # This fixes the '?????' issue
        clean_content = sanitize_text_for_pdf(content)
        lines = clean_content.split('\n')
        
        for line in lines:
            if text_y < bottom_margin:
                c.showPage()
                page_num += 1
                draw_header(c, width, height, target, tool_name)
                draw_footer(c, width, height, page_num)
                draw_watermark(c, width, height)
                text_y = height - 130 
                # Re-apply font settings for new page
                c.setFont("Courier", 9)
                c.setFillColor(TEXT_DARK)
            
            # Wrap text carefully
            wrapped_lines = textwrap.wrap(line, width=95)
            
            for wrapped_line in wrapped_lines:
                if ":" in wrapped_line and not any(x in wrapped_line for x in ["|", "[", "+", "="]):
                     c.setFont("Courier-Bold", 9)
                     c.drawString(50, text_y, wrapped_line)
                     c.setFont("Courier", 9)
                else:
                     c.drawString(50, text_y, wrapped_line)
                
                text_y -= line_height
                
                if text_y < bottom_margin:
                     c.showPage()
                     page_num += 1
                     draw_header(c, width, height, target, tool_name)
                     draw_footer(c, width, height, page_num)
                     draw_watermark(c, width, height)
                     text_y = height - 130
                     c.setFont("Courier", 9)
                     c.setFillColor(TEXT_DARK)

        c.save()
        return True
        
    except Exception as e:
        print(f"[!] PDF Error: {e}")
        return False