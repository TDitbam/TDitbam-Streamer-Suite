#!/bin/bash
# TDitbam Streamer Suite - Unified Run Script (Linux)

cd "$(dirname "$0")"

# 1. Try to run the application first
python3 main.py

# 2. If it fails, identify the cause
if [ $? -ne 0 ]; then
    echo ""
    echo "[!] Application failed or Python3 is missing. Diagnosing..."
    
    if ! command -v python3 &> /dev/null; then
        echo "[!] Python3 not found. Installing via apt..."
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y python3 python3-pip
            echo "[*] Python3 installed. Retrying..."
            python3 main.py
        else
            echo "[!] Package manager 'apt' not found. Please install python3 manually."
        fi
    else
        # Python3 exists, so check for missing libraries
        if [ -f "requirements.txt" ]; then
            echo "[!] Missing libraries detected. Installing requirements..."
            python3 -m pip install -r requirements.txt
            
            echo "[*] Retrying application..."
            python3 main.py
        else
            echo "[!] requirements.txt not found. Cannot auto-install libraries."
        fi
    fi
fi
