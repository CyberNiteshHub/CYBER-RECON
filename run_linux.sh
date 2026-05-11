#!/bin/bash

# --- 1. DIRECTORY SETUP (Future Proofing) ---
# Script jahan bhi rakhi ho, wahi se run karegi. Path ka issue nahi aayega.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================="
echo "     CYBER RECON TOOLKIT - PRO LAUNCHER"
echo "=================================================="

# --- 2. VARIABLE DEFINITIONS ---
# Hum direct binaries ko point karenge taaki 'activate' ki zarurat na pade.
VENV_PATH="$DIR/venv"
PYTHON_BIN="$VENV_PATH/bin/python3"
PIP_BIN="$VENV_PATH/bin/pip"

# --- 3. VIRTUAL ENVIRONMENT CHECK ---
if [ ! -d "$VENV_PATH" ]; then
    echo "[INFO] Creating Virtual Environment for the first time..."
    # Try creating venv
    python3 -m venv "$VENV_PATH"
    
    # Error Handling: Agar venv nahi bana (Common issue in Kali/Ubuntu)
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        echo "[FIX] Please run: sudo apt install python3-venv -y"
        exit 1
    fi
fi

# --- 4. DEPENDENCY CHECK (Smart Install) ---
# Ye har baar check karega. Agar aap future me requirements.txt me kuch add karenge
# to ye automatically use install kar lega bina error diye.
echo "[INFO] Checking System & Python Dependencies..."

if [ -f "requirements.txt" ]; then
    REQ_FILE="requirements.txt"
elif [ -f "backend/requirements.txt" ]; then
    REQ_FILE="backend/requirements.txt"
else
    echo "[ERROR] requirements.txt not found (expected at repo root)."
    exit 1
fi
"$PIP_BIN" install -r "$REQ_FILE" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[WARNING] Some Python libraries failed to install. Check internet connection."
else
    echo "[OK] Python Dependencies Verified."
fi

# --- 5. BROWSER LAUNCHER (Sudo-Safe Mode) ---
# Agar aap 'sudo' use kar rahe hain, to browser root se nahi khulna chahiye.
# Ye logic check karega ki asli user kaun hai aur uske naam par browser kholega.
TARGET_URL="http://127.0.0.1:5000"

echo "[INFO] Launching Interface..."
if [ -n "$SUDO_USER" ]; then
    # Run browser as the original non-root user
    su -c "xdg-open $TARGET_URL" "$SUDO_USER" > /dev/null 2>&1 &
else
    # Run normally
    xdg-open "$TARGET_URL" > /dev/null 2>&1 &
fi

# --- 6. START BACKEND SERVER ---
echo "[INFO] Starting CyberRecon Server..."
echo "--------------------------------------------------"
# Using the venv python directly guarantees imports work
"$PYTHON_BIN" backend/app.py