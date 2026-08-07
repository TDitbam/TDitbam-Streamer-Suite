import sys
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Ensure working directory is the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Add script directory to sys.path for robust module imports
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

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

    # Acquire the process lock before importing GUI/TTS modules. This prevents
    # a duplicate launch from initializing audio, collectors, tray icons, or
    # log handlers before it is rejected.
    from core.single_instance import SingleInstance

    instance = SingleInstance()
    if not instance.acquire():
        if os.name != "nt":
            print("TDitbam Streamer Suite is already running.")
        return

    try:
        import customtkinter as ctk
        from core.tts_engine import ChatTTSEngine
        from gui.app import App

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize Core Engine
        engine = ChatTTSEngine()
        
        # Initialize Main App
        app = App(engine, instance_guard=instance)
        
        # Start the application
        app.run()
    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Startup Error", f"Failed to start application:\n{e}")
        raise
    finally:
        instance.release()

if __name__ == "__main__":
    main()
