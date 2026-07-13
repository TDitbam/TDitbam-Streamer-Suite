import customtkinter as ctk
import configparser
import threading
import os
import sys
import logging
import pystray
from pystray import MenuItem as item
from PIL import Image
from core.tts_engine import ChatTTSEngine
from core.app_logger import get_logger, get_config_path, logger as base_logger
from optimizer.optimizer_core.config_loader import load_config as load_opt_config

from .sidebar import SidebarFrame
from .dashboard import DashboardFrame
from .chat_frame import ChatFrame
from .optimizer_frame import OptimizerFrame
from .cleanup_frame import CleanupFrame
from .windows_tools_frame import WindowsToolsFrame
from .settings_frame import SettingsFrame
from .logic import AppLogic

class GuiLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            try:
                self.text_widget.configure(state="normal")
                self.text_widget.insert("end", msg + "\n")
                self.text_widget.see("end")
                self.text_widget.configure(state="disabled")
            except:
                pass
        self.text_widget.after(0, append)

class App(ctk.CTk):
    def __init__(self, engine):
        super().__init__()
        self.title("Streamer Suite")
        self.geometry("1100x800")
        
        self.engine = engine
        self.logger = get_logger("App")
        
        # Load Configs
        self.config = configparser.ConfigParser()
        if os.path.exists(get_config_path()):
            self.config.read(get_config_path(), encoding="utf-8")
        
        self.opt_config = load_opt_config()
        self.opt_running = False
        self.opt_stop_event = threading.Event()
        
        # Variables for Optimizer / System
        self.opt_auto_shutdown = ctk.BooleanVar(value=self.opt_config["Settings"].getboolean("auto_shutdown", fallback=False))
        self.opt_shutdown_time = ctk.StringVar(value=self.opt_config["Settings"].get("shutdown_time", fallback="23:59"))
        
        # System Tray Setup
        self.protocol('WM_DELETE_WINDOW', self.withdraw_to_tray)
        self.create_tray_icon()
        
        # Fonts
        self.title_font = ctk.CTkFont(size=24, weight="bold")
        self.bold_font = ctk.CTkFont(size=14, weight="bold")
        self.default_font = ctk.CTkFont(size=13)
        
        # Variables for Chat-TTS
        s = "settings"
        tts_old = "tts"
        self.yt_enabled = ctk.StringVar(value=self.config.get(s, "yt_enabled", fallback=self.config.get(tts_old, "yt_enabled", fallback="True")))
        self.tw_enabled = ctk.StringVar(value=self.config.get(s, "tw_enabled", fallback=self.config.get(tts_old, "tw_enabled", fallback="False")))
        self.tk_enabled = ctk.StringVar(value=self.config.get(s, "tk_enabled", fallback=self.config.get(tts_old, "tk_enabled", fallback="False")))
        self.auto_translate = ctk.StringVar(value=self.config.get(s, "auto_translate", fallback=self.config.get(tts_old, "auto_translate", fallback="False")))
        self.profanity_enabled = ctk.StringVar(value=self.config.get(s, "profanity_enabled", fallback=self.config.get(tts_old, "profanity_enabled", fallback="False")))
        
        # Voice compatibility
        voice_val = self.config.get(s, "voice", fallback=self.config.get(tts_old, "voice", fallback=self.config.get(s, "VOICE", fallback="th-TH-PremwadeeNeural")))
        self.voice_var = ctk.StringVar(value=voice_val)
        
        # General App Settings
        self.start_minimized = ctk.BooleanVar(value=self.config.getboolean(s, "start_minimized", fallback=False))
        self.run_on_startup = ctk.BooleanVar(value=self.config.getboolean(s, "run_on_startup", fallback=False))
        
        # Initialize Logic
        self.logic = AppLogic(self, self.engine)
        self.logic.sync_shutdown_task()
        self.logic.sync_startup_task()
        
        # UI Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = SidebarFrame(self, self.show_frame)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        self.frames = {}
        for F in (DashboardFrame, ChatFrame, OptimizerFrame, CleanupFrame, WindowsToolsFrame, SettingsFrame):
            page_name = F.__name__.replace("Frame", "").lower()
            frame = F(self.container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        # Setup Logger Redirect
        self.log_handler = GuiLogHandler(self.frames["dashboard"].log_box)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))
        base_logger.addHandler(self.log_handler)
        
        # Initial topology stats update
        self.after(500, self.logic.update_topology_stats)
        
        self._setup_listeners()
        self._setup_shortcut_handler()
        self.show_frame("dashboard")
        
        # Auto-minimize to system tray if configured
        if self.start_minimized.get():
            self.after(200, self.withdraw_to_tray)

    def _setup_listeners(self):
        """Setup listeners for real-time config updates."""
        for var in [self.auto_translate, self.profanity_enabled, self.voice_var]:
            var.trace_add("write", lambda *args: self.logic.apply_realtime_config())

    def _setup_shortcut_handler(self):
        """Register layout-independent global keyboard shortcuts for Ctrl+C, Ctrl+V, etc."""
        def handle_shortcuts(event):
            # Check if Control modifier (mask 4) is active on Windows/Linux
            ctrl = (event.state & 0x0004) != 0
            
            if ctrl:
                widget = event.widget
                if not widget:
                    return
                
                # Determine if widget is normal/editable
                state = "normal"
                if hasattr(widget, "cget"):
                    try:
                        state = str(widget.cget("state"))
                    except:
                        pass
                
                # Virtual keycodes for standard letter keys (layout independent)
                # 65 = A, 67 = C, 86 = V, 88 = X, 90 = Z
                if event.keycode == 86:  # V
                    if state == "normal":
                        widget.event_generate("<<Paste>>")
                        return "break"
                elif event.keycode == 67:  # C
                    widget.event_generate("<<Copy>>")
                    return "break"
                elif event.keycode == 88:  # X
                    if state == "normal":
                        widget.event_generate("<<Cut>>")
                        return "break"
                elif event.keycode == 65:  # A
                    # Select All
                    if widget.winfo_class() == "Text":
                        widget.tag_add("sel", "1.0", "end")
                    elif hasattr(widget, "select_range"):
                        widget.select_range(0, "end")
                        widget.icursor("end")
                    return "break"
                elif event.keycode == 90:  # Z
                    if state == "normal":
                        try:
                            widget.edit_undo()
                        except:
                            widget.event_generate("<<Undo>>")
                        return "break"

        self.bind_all("<Key>", handle_shortcuts, "+")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    # --- System Tray Methods ---
    def create_tray_icon(self):
        icon_path = 'gui/icon.ico'
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
        else:
            image = Image.new('RGB', (64, 64), color=(40, 167, 69))
            
        menu = (item('Open Streamer Suite', self.show_from_tray, default=True),
                item('Exit', self.exit_app))
        self.tray_icon = pystray.Icon("StreamerSuite", image, "Streamer Suite", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def withdraw_to_tray(self):
        self.withdraw()

    def show_from_tray(self, icon=None, item=None):
        self.after(0, self.deiconify)
        self.after(0, self.focus_force)

    def exit_app(self, icon=None, item=None):
        self.logger.info("Exiting application...")
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.engine.stop()
        self.opt_stop_event.set()
        self.quit()
        sys.exit(0)

    # Delegate logic methods for easier access from frames
    def toggle_tts(self): self.logic.toggle_tts()
    def toggle_optimizer(self): self.logic.toggle_optimizer()
    def save_chat_settings(self): self.logic.save_chat_settings()
    def save_opt_settings(self): self.logic.save_opt_settings()
    def save_app_settings(self): self.logic.save_app_settings()
    def refresh_opt_list(self): self.logic.refresh_opt_list()
    def refresh_path_list(self): self.logic.refresh_path_list()
    def add_opt_target(self): self.logic.add_opt_target()
    def remove_opt_target(self, name): self.logic.remove_opt_target(name)
    def add_opt_path(self): self.logic.add_opt_path()
    def remove_opt_path(self, path): self.logic.remove_opt_path(path)
    def run_junk_cleanup(self): self.logic.run_junk_cleanup()
    def update_topology_stats(self): self.logic.update_topology_stats()

    def run(self):
        self.mainloop()
