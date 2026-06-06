import sys
import os
import ctypes
import customtkinter as ctk
from core.tts_engine import ChatTTSEngine
from gui.app import App

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Administrator Elevation Logic for Windows
    if os.name == 'nt':
        if not is_admin():
            print("[*] Requesting Administrator privileges...")
            executable = sys.executable
            params = f'"{os.path.abspath(sys.argv[0])}" ' + ' '.join(sys.argv[1:])
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
            except Exception as e:
                print(f"[!] Failed to elevate: {e}")
            sys.exit(0)

    # Set theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Initialize Core Engine
    engine = ChatTTSEngine()
    
    # Initialize Main App
    app = App(engine)
    
    # Start the application
    app.run()

if __name__ == "__main__":
    main()
