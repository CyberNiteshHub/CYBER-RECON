// --- 🌍 GLOBAL STATE ---
let currentResult = null;
let currentTool = null;
let currentTarget = null;
let mapInstance = null; // Leaflet Map Object

// 🔥 VOICE & AI GLOBALS
let hindiSpeechText = ""; // Hindi script store karne ke liye
let synth = window.speechSynthesis; // Browser ka bolne wala engine
let currentUtterance = null; // Current speech object

// --- 🏗️ DOM ELEMENTS ---
const outputArea = document.getElementById('outputArea');
const btnReport = document.getElementById('btnReport');
const btnAI = document.getElementById('btnAI');
const geoContainer = document.getElementById('geo-visuals');
const aiPanel = document.getElementById('ai-panel');
const aiOutput = document.getElementById('aiOutput');

// --- 🛠️ HELPER FUNCTIONS ---

// 1. Terminal Output Setter
function setOutput(text, isError = false) {
    // Safety check for null text
    if (!text) text = "";
    if (typeof text !== 'string') text = JSON.stringify(text, null, 2);

    outputArea.textContent = text;
    outputArea.style.color = isError ? '#ff5f56' : '#e0e0e0';
    outputArea.scrollTop = outputArea.scrollHeight;
}

// 2. Loading State Animation
function setLoading(msg) {
    outputArea.textContent = `[PROCESS] ${msg}...\n[STATUS] Initializing protocols...\n[STATUS] Establishing secure connection... please wait.`;
    outputArea.style.color = '#ffff00'; // Hacker Yellow
    
    // Reset UI components
    if (geoContainer) geoContainer.style.display = 'none';
    if (aiPanel) aiPanel.style.display = 'none';
    btnAI.disabled = true; 
    btnReport.disabled = true;
    
    // Stop any active voice
    stopVoice();
}

// 3. Typewriter Effect (🔥 CRASH PROOF FIXED)
let typeWriterTimeout = null;
function typeWriter(element, text, speed = 10) {
    if (typeWriterTimeout) clearTimeout(typeWriterTimeout);
    
    // 🔥 SAFETY LAYER 1: Force convert to string to prevent .charAt error
    if (text === null || text === undefined) text = "";
    text = String(text); 

    element.textContent = "";
    let i = 0;
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            element.parentElement.scrollTop = element.parentElement.scrollHeight;
            typeWriterTimeout = setTimeout(type, speed);
        }
    }
    type();
}

// --- 🚀 MAIN LOGIC: RUN TOOL ---
async function runTool() {
    if (!navigator.onLine) {
        setOutput("ERROR: No Internet Connection. Cannot execute tools.", true);
        return;
    }

    const target = document.getElementById('targetInput').value.trim();
    const tool = document.getElementById('toolSelect').value;

    if (!target) {
        setOutput("ERROR: Please enter a Target IP or Domain.", true);
        return;
    }

    setLoading(`Executing ${tool.toUpperCase()} on ${target}`);

    try {
        // 🔥 NEW: SQL Injection has separate endpoint
        if (tool === 'sqli') {
            await runSQLiScan(target);
            return;
        }

        const response = await fetch(`/api/run?target=${encodeURIComponent(target)}&tool=${tool}`);
        const data = await response.json();

        if (data.ok) {
            setOutput(data.data);
            
            currentResult = data.data;
            currentTool = tool;
            currentTarget = target;
            
            btnReport.disabled = false;
            btnAI.disabled = false; 

            if (tool === 'geoip' && data.meta) {
                showMap(data.meta.lat, data.meta.lon, data.meta.address, data.meta.map_link);
            } else {
                if (geoContainer) geoContainer.style.display = 'none';
            }

        } else {
            setOutput(`[FAILED] ${data.error}`, true);
        }
    } catch (err) {
        setOutput(`[SYSTEM ERROR] Connection Refused. Ensure Backend is running.\nDetails: ${err}`, true);
    }
}

// --- 🔐 SQL INJECTION SCAN (NEW FUNCTION) ---
async function runSQLiScan(targetUrl) {
    // NEW FUNCTION: Run SQL Injection vulnerability scan
    // Sends POST request to /api/sqli endpoint
    
    if (!targetUrl.startsWith("http")) {
        targetUrl = "http://" + targetUrl;
    }

    try {
        const response = await fetch('/api/sqli', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target: targetUrl
            })
        });

        const data = await response.json();

        if (data.ok) {
            setOutput(data.data);
            
            currentResult = data.data;
            currentTool = 'sqli';
            currentTarget = targetUrl;
            
            btnReport.disabled = false;
            btnAI.disabled = false;
            
            // Hide geo-location containers for SQL injection
            if (geoContainer) geoContainer.style.display = 'none';
            
        } else {
            setOutput(`[FAILED] ${data.error}`, true);
        }
    } catch (err) {
        setOutput(`[SYSTEM ERROR] SQL Injection scan failed.\nDetails: ${err}`, true);
    }
}

// --- 🧠 AI LOGIC: ANALYZE RESULT (🔥 CRASH PROOF FIXED) ---
async function analyzeWithAI() {
    if (!navigator.onLine) {
        alert("Internet required for AI Analysis.");
        return;
    }

    if (!currentResult || !currentTool) return;

    aiPanel.style.display = 'block';
    aiOutput.textContent = "🔄 Uploading data to Neural Network... Verifying Integrity...";
    aiOutput.style.color = "#bd00ff"; 
    
    // Reset Voice Buttons
    if(document.getElementById('btnSpeak')) document.getElementById('btnSpeak').style.display = 'none';
    if(document.getElementById('btnStop')) document.getElementById('btnStop').style.display = 'none';
    if(document.getElementById('voiceWave')) document.getElementById('voiceWave').style.display = 'none';

    aiPanel.scrollIntoView({ behavior: 'smooth' });

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool: currentTool,
                content: currentResult
            })
        });

        const data = await response.json();

        if (data.ok) {
            aiOutput.style.color = "#dcb3ff";
            
            // 🔥 SAFETY LAYER 2: Robust Data Extraction
            let displayText = "Analysis Complete.";
            
            // Check agar backend ne sahi JSON bheja hai
            if (data.data && data.data.display_text) {
                displayText = data.data.display_text;
            } else if (typeof data.data === 'string') {
                // Fallback agar sirf text aya
                displayText = data.data;
            }
            
            // Ab ye kabhi crash nahi hoga
            typeWriter(aiOutput, displayText, 5);
            
            // Store Hindi Speech safely
            hindiSpeechText = "";
            if (data.data && data.data.speech_text) {
                hindiSpeechText = data.data.speech_text;
            }

            // Button tabhi dikhao jab hindi text maujood ho
            if (hindiSpeechText && document.getElementById('btnSpeak')) {
                document.getElementById('btnSpeak').style.display = 'flex';
            }

        } else {
            aiOutput.textContent = `[AI ERROR] ${data.error}`;
            aiOutput.style.color = "#ff0055";
        }

    } catch (err) {
        console.error("AI Fetch Error:", err);
        aiOutput.textContent = `[CONNECTION ERROR] Could not reach AI Engine.\nDetails: ${err}`;
        aiOutput.style.color = "#ff0055";
    }
}

// --- 🔊 VOICE CONTROL FUNCTIONS ---

function playVoice() {
    if (!hindiSpeechText) return;

    synth.cancel(); // Stop previous

    currentUtterance = new SpeechSynthesisUtterance(hindiSpeechText);
    
    // Voice Selection (Hindi)
    const voices = synth.getVoices();
    const hindiVoice = voices.find(v => v.lang.includes('hi') || v.name.includes('Hindi') || v.name.includes('Google हिन्दी'));
    
    if (hindiVoice) {
        currentUtterance.voice = hindiVoice;
    }
    
    currentUtterance.lang = 'hi-IN';
    currentUtterance.rate = 1.0;
    currentUtterance.pitch = 1.0;

    // UI Updates
    document.getElementById('btnSpeak').style.display = 'none';
    document.getElementById('btnStop').style.display = 'flex';
    document.getElementById('voiceWave').style.display = 'flex';

    currentUtterance.onend = function() { resetVoiceUI(); };
    currentUtterance.onerror = function() { resetVoiceUI(); };

    synth.speak(currentUtterance);
}

function stopVoice() {
    synth.cancel();
    resetVoiceUI();
}

function resetVoiceUI() {
    if(document.getElementById('btnSpeak')) document.getElementById('btnSpeak').style.display = 'flex';
    if(document.getElementById('btnStop')) document.getElementById('btnStop').style.display = 'none';
    if(document.getElementById('voiceWave')) document.getElementById('voiceWave').style.display = 'none';
}

// --- 🗺️ MAP RENDERER ---
function showMap(lat, lon, address, link) {
    if (!geoContainer) return;

    geoContainer.style.display = 'flex'; 
    document.getElementById('geoAddress').textContent = address;
    document.getElementById('geoLink').value = link;

    if (mapInstance) mapInstance.remove(); 

    mapInstance = L.map('map').setView([lat, lon], 13);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap contributors © CARTO',
        maxZoom: 19
    }).addTo(mapInstance);

    L.marker([lat, lon]).addTo(mapInstance)
        .bindPopup(`<b>TARGET ACQUIRED</b><br>${address}`)
        .openPopup();
        
    setTimeout(() => { mapInstance.invalidateSize(); }, 300);
}

// --- 📋 COPY LINK ---
function copyGeoLink() {
    const copyText = document.getElementById("geoLink");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
    
    const btn = document.querySelector('.btn-copy');
    const originalText = btn.textContent;
    
    btn.textContent = "COPIED!";
    btn.style.color = "#00ff41";
    btn.style.borderColor = "#00ff41";
    
    setTimeout(() => { 
        btn.textContent = originalText; 
        btn.style.color = "#fff";
        btn.style.borderColor = "#555";
    }, 2000);
}

// --- 📄 DOWNLOAD REPORT ---
async function downloadReport() {
    if (!currentResult) return;
    setLoading("Generating Forensic PDF Report");

    try {
        const response = await fetch('/api/report/single', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target: currentTarget,
                tool: currentTool,
                content: currentResult
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Report_${currentTool}_${currentTarget}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setOutput(currentResult + "\n\n[SUCCESS] PDF Report Exported Successfully!");
        } else {
            setOutput("Error generating report.", true);
        }
    } catch (err) {
        setOutput(`Download failed: ${err}`, true);
    }
}

// --- ☢️ FULL SCAN ---
async function runFullScan() {
    if (!navigator.onLine) {
        setOutput("ERROR: No Internet Connection. Full Recon Aborted.", true);
        return;
    }

    const target = document.getElementById('targetInput').value.trim();
    if (!target) {
        setOutput("ERROR: Target required for Full Scan.", true);
        return;
    }

    setLoading(`INITIATING FULL SYSTEM RECONNAISSANCE on ${target}\n(This involves Nmap, GeoIP, Whois, etc.)\nPlease be patient...`);
    
    if (geoContainer) geoContainer.style.display = 'none';
    if (aiPanel) aiPanel.style.display = 'none';

    try {
        const response = await fetch('/api/report/all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: target })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `FULL_RECON_${target}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setOutput(`[COMPLETED] Full Recon Finished.\n[SUCCESS] Master Report Downloaded.`);
        } else {
            const errData = await response.json();
            setOutput(`[FAILED] Full scan error: ${errData.error}`, true);
        }
    } catch (err) {
        setOutput(`[SYSTEM ERROR] ${err}`, true);
    }
}

// --- 📡 REAL-TIME INTERNET MONITOR ---
const offlineOverlay = document.getElementById('offline-overlay');
let offlineTimer = null; 

function updateConnectionStatus() {
    if (navigator.onLine) {
        if (offlineTimer) {
            clearTimeout(offlineTimer);
            offlineTimer = null;
        }
        if (offlineOverlay && offlineOverlay.style.display === 'flex') {
            offlineOverlay.style.display = 'none';
        }
    } else {
        if (!offlineTimer) {
            offlineTimer = setTimeout(() => {
                if (!navigator.onLine && offlineOverlay) {
                     offlineOverlay.style.display = 'flex'; 
                }
                offlineTimer = null;
            }, 2000); 
        }
    }
}

window.addEventListener('online', updateConnectionStatus);
window.addEventListener('offline', updateConnectionStatus);
updateConnectionStatus();

setInterval(() => {
    if (!navigator.onLine) {
        updateConnectionStatus();
    }
}, 3000);