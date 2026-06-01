import customtkinter as ctk
import configparser
import sys
import os
import logging
import threading
from tkinter import filedialog
from PIL import Image
import pystray
from pystray import MenuItem as item

# Add core directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'optimizer'))

from optimizer_core.optimizer_engine import optimize_processes
from optimizer_core.config_loader import load_config as load_opt_config, save_config as save_opt_config, get_targets as get_opt_targets
from optimizer_core.cpu_topology import split_p_e_cores
from optimizer_core.cleaner import clean_junk

from core.tts_engine import ChatTTSEngine
from core.app_logger import get_logger, logger as base_logger

logger = get_logger("GUI")
CONFIG_FILE = "config.ini"

class GuiLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg + "\n")
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
        self.text_widget.after(0, append)

class StreamerSuiteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TDitbam Streamer Suite Pro v3.1.0")
        self.geometry("1100x850")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Data & Engines ---
        self.engine = ChatTTSEngine()
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding="utf-8")
        
        self.opt_running = False
        self.opt_stop_event = threading.Event()
        self.opt_config = load_opt_config()

        # System Tray Setup
        self.protocol('WM_DELETE_WINDOW', self.withdraw_to_tray)
        self.create_tray_icon()

        # --- Layout Setup ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        
        # Main Containers
        self.dashboard_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.optimizer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cleanup_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.setup_dashboard_ui()
        self.setup_chat_ui()
        self.setup_optimizer_ui()
        self.setup_cleanup_ui()
        
        # Setup Logger Redirect
        self.log_handler = GuiLogHandler(self.log_box)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))
        base_logger.addHandler(self.log_handler)

        self.show_frame(self.dashboard_frame)
        logger.info("Streamer Suite Pro v3.1.0 Initialized")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1E1E1E")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar_frame, text="STREAMER SUITE", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=40)
        
        btn_style = {"height": 45, "corner_radius": 8, "fg_color": "transparent", "hover_color": "#333333", "anchor": "w"}
        self.btn_dash = ctk.CTkButton(self.sidebar_frame, text="🏠 Dashboard", **btn_style, command=lambda: self.show_frame(self.dashboard_frame))
        self.btn_dash.pack(pady=5, padx=10, fill="x")
        self.btn_chat = ctk.CTkButton(self.sidebar_frame, text="💬 Chat-TTS", **btn_style, command=lambda: self.show_frame(self.chat_frame))
        self.btn_chat.pack(pady=5, padx=10, fill="x")
        self.btn_opt = ctk.CTkButton(self.sidebar_frame, text="🚀 Optimizer", **btn_style, command=lambda: self.show_frame(self.optimizer_frame))
        self.btn_opt.pack(pady=5, padx=10, fill="x")
        self.btn_clean = ctk.CTkButton(self.sidebar_frame, text="🧹 Cleanup", **btn_style, command=lambda: self.show_frame(self.cleanup_frame))
        self.btn_clean.pack(pady=5, padx=10, fill="x")

    def setup_dashboard_ui(self):
        # KPI Cards (v3.1.0 Style)
        top_stats = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        top_stats.pack(fill="x", pady=10)
        
        self.status_card = ctk.CTkFrame(top_stats, corner_radius=15, fg_color="#2D2D2D", height=100)
        self.status_card.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(self.status_card, text="SYSTEM STATUS", font=("Helvetica", 10)).pack(pady=(15, 0))
        self.status_label = ctk.CTkLabel(self.status_card, text="IDLE", font=("Helvetica", 24, "bold"), text_color="#ABB2BF")
        self.status_label.pack(pady=(0, 15))

        card_p = ctk.CTkFrame(top_stats, corner_radius=15, fg_color="#2D2D2D")
        card_p.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(card_p, text="P-CORES", font=("Helvetica", 10)).pack(pady=(15, 0))
        self.pcore_lbl = ctk.CTkLabel(card_p, text="0", font=("Helvetica", 30, "bold"), text_color="#28a745")
        self.pcore_lbl.pack(pady=(0, 15))

        card_e = ctk.CTkFrame(top_stats, corner_radius=15, fg_color="#2D2D2D")
        card_e.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(card_e, text="E-CORES", font=("Helvetica", 10)).pack(pady=(15, 0))
        self.ecore_lbl = ctk.CTkLabel(card_e, text="0", font=("Helvetica", 30, "bold"), text_color="#17a2b8")
        self.ecore_lbl.pack(pady=(0, 15))

        # Main Controls
        ctrl_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="#2D2D2D", corner_radius=15)
        ctrl_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(ctrl_frame, text="Master Control Panel", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        self.btn_toggle_tts = ctk.CTkButton(ctrl_frame, text="START CHAT-TTS", height=50, fg_color="#28a745", 
                                            font=("Helvetica", 14, "bold"), command=self.toggle_tts)
        self.btn_toggle_tts.pack(side="left", expand=True, fill="x", padx=20, pady=20)
        
        self.btn_toggle_opt = ctk.CTkButton(ctrl_frame, text="START OPTIMIZER", height=50, fg_color="#17a2b8", 
                                            font=("Helvetica", 14, "bold"), command=self.toggle_optimizer)
        self.btn_toggle_opt.pack(side="left", expand=True, fill="x", padx=20, pady=20)

        # Log Box
        self.log_box = ctk.CTkTextbox(self.dashboard_frame, corner_radius=15, fg_color="#1E1E1E", border_width=1, border_color="#333333")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_box.configure(state="disabled")
        
        self.update_topology_stats()

    def setup_chat_ui(self):
        self._init_chat_vars()
        scroll = ctk.CTkScrollableFrame(self.chat_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sections for Platform Config
        for platform, var, entry_attr, placeholder in [
            ("YouTube Live", self.yt_enabled, "entry_yt", "Video ID or URL"),
            ("Twitch Chat", self.tw_enabled, "entry_tw", "Channel Name"),
            ("TikTok Live", self.tk_enabled, "entry_tk", "@username")
        ]:
            f = ctk.CTkFrame(scroll, fg_color="#2D2D2D", corner_radius=10)
            f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=platform, font=("Helvetica", 12, "bold")).pack(anchor="w", padx=15, pady=5)
            inner = ctk.CTkFrame(f, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=(0, 10))
            ctk.CTkCheckBox(inner, text="Enabled", variable=var, onvalue="True", offvalue="False").pack(side="left")
            entry = ctk.CTkEntry(inner, placeholder_text=placeholder, width=350)
            setattr(self, entry_attr, entry)
            entry.insert(0, self.config.get("settings", entry_attr.replace("entry_", "YOUTUBE_VIDEO_ID") if platform == "YouTube Live" else entry_attr.replace("entry_", "tw_channel") if platform == "Twitch Chat" else "tk_username", fallback=""))
            entry.pack(side="right")

        # Voice & General Settings
        v_f = ctk.CTkFrame(scroll, fg_color="#2D2D2D", corner_radius=10)
        v_f.pack(fill="x", pady=5)
        
        # First row: Voice and Translate
        row1 = ctk.CTkFrame(v_f, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(row1, text="Voice Model:").pack(side="left")
        self.voice_menu = ctk.CTkOptionMenu(row1, values=["th-TH-PremwadeeNeural", "th-TH-NiwatNeural"], variable=self.voice_var)
        self.voice_menu.pack(side="left", padx=10)
        ctk.CTkCheckBox(row1, text="Auto-Translate (TH)", variable=self.auto_translate, onvalue="True", offvalue="False").pack(side="left", padx=10)
        ctk.CTkCheckBox(row1, text="Filter Profanity", variable=self.profanity_enabled, onvalue="True", offvalue="False").pack(side="left", padx=10)

        # Second row: Delays
        row2 = ctk.CTkFrame(v_f, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(row2, text="Delay/Char:").pack(side="left")
        self.entry_delay_char = ctk.CTkEntry(row2, width=60)
        self.entry_delay_char.insert(0, self.config.get("settings", "delay_per_char", fallback="0.03"))
        self.entry_delay_char.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Max Delay:").pack(side="left", padx=(10, 0))
        self.entry_max_delay = ctk.CTkEntry(row2, width=60)
        self.entry_max_delay.insert(0, self.config.get("settings", "max_delay", fallback="2.0"))
        self.entry_max_delay.pack(side="left", padx=5)

        # Profanity List / Custom Filter
        ctk.CTkLabel(v_f, text="Custom Message Filter (Comma separated):", font=("Helvetica", 11)).pack(padx=15, pady=(10, 0), anchor="w")
        self.textbox_filter = ctk.CTkTextbox(v_f, height=80, fg_color="#1E1E1E")
        self.textbox_filter.pack(fill="x", padx=15, pady=10)

    def setup_optimizer_ui(self):
        # Settings (v3.1.0 Style)
        s_f = ctk.CTkFrame(self.optimizer_frame, fg_color="#2D2D2D", corner_radius=15)
        s_f.pack(fill="x", pady=10, padx=20)
        
        self.opt_exclude_c0 = ctk.BooleanVar(value=self.opt_config["Settings"].getboolean("exclude_core_0", fallback=True))
        ctk.CTkSwitch(s_f, text="Exclude Core 0", variable=self.opt_exclude_c0, command=self.save_opt_settings).pack(pady=5, padx=20, anchor="w")
        self.opt_disable_smt = ctk.BooleanVar(value=self.opt_config["Settings"].getboolean("disable_smt", fallback=False))
        ctk.CTkSwitch(s_f, text="Disable SMT", variable=self.opt_disable_smt, command=self.save_opt_settings).pack(pady=5, padx=20, anchor="w")

        # Tabs for Games and Directories (New in v3.1.0)
        self.opt_tabs = ctk.CTkTabview(self.optimizer_frame, corner_radius=15)
        self.opt_tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.setup_games_tab(self.opt_tabs.add("Games"))
        self.setup_dirs_tab(self.opt_tabs.add("Directories"))

    def setup_games_tab(self, tab):
        self.g_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.g_scroll.pack(fill="both", expand=True)
        ui = ctk.CTkFrame(tab, fg_color="transparent"); ui.pack(fill="x", pady=5)
        self.entry_new_game = ctk.CTkEntry(ui, placeholder_text="game.exe")
        self.entry_new_game.pack(side="left", expand=True, fill="x")
        self.opt_prio_menu = ctk.CTkOptionMenu(ui, values=["P-CORE", "E-CORE", "NORMAL"], width=100)
        self.opt_prio_menu.pack(side="left", padx=5)
        ctk.CTkButton(ui, text="Add", width=60, command=self.add_opt_target).pack(side="right")
        self.refresh_opt_list()

    def setup_dirs_tab(self, tab):
        self.d_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.d_scroll.pack(fill="both", expand=True)
        ctk.CTkButton(tab, text="Add Managed Directory", command=self.add_opt_path).pack(fill="x", pady=5)

    def setup_cleanup_ui(self):
        main_c = ctk.CTkFrame(self.cleanup_frame, fg_color="#2D2D2D", corner_radius=20)
        main_c.pack(pady=30, padx=30, fill="both", expand=True)

        # Maintenance Section (New in v3.1.0)
        m_frame = ctk.CTkFrame(main_c, fg_color="transparent")
        m_frame.pack(fill="x", pady=10, padx=20)
        
        self.opt_auto_clean = ctk.BooleanVar(value=self.opt_config["Settings"].getboolean("auto_cleanup", fallback=False))
        ctk.CTkSwitch(m_frame, text="Auto Junk Cleanup", variable=self.opt_auto_clean, command=self.save_opt_settings).pack(side="left", padx=10)
        
        timer_frame = ctk.CTkFrame(m_frame, fg_color="transparent")
        timer_frame.pack(side="right", padx=10)
        ctk.CTkLabel(timer_frame, text="Interval (min):").pack(side="left")
        self.opt_clean_interval = ctk.StringVar(value=self.opt_config["Settings"].get("cleanup_interval", "1440"))
        self.entry_clean_int = ctk.CTkEntry(timer_frame, textvariable=self.opt_clean_interval, width=60)
        self.entry_clean_int.pack(side="left", padx=5)
        ctk.CTkButton(timer_frame, text="Apply", width=60, command=self.save_opt_settings).pack(side="left")

        ctk.CTkButton(main_c, text="SCAN & CLEAN JUNK", height=60, fg_color="#dc3545", font=("Helvetica", 16, "bold"), command=self.run_junk_cleanup).pack(pady=20)
        self.clean_log = ctk.CTkTextbox(main_c, fg_color="#1E1E1E", corner_radius=10)
        self.clean_log.pack(fill="both", expand=True, padx=20, pady=20)

    # --- Logic ---
    def show_frame(self, frame):
        for f in [self.dashboard_frame, self.chat_frame, self.optimizer_frame, self.cleanup_frame]: f.grid_forget()
        frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def _init_chat_vars(self):
        self.yt_enabled = ctk.StringVar(value=self.config.get("settings", "yt_enabled", fallback="True"))
        self.tw_enabled = ctk.StringVar(value=self.config.get("settings", "tw_enabled", fallback="False"))
        self.tk_enabled = ctk.StringVar(value=self.config.get("settings", "tk_enabled", fallback="False"))
        self.auto_translate = ctk.StringVar(value=self.config.get("settings", "auto_translate", fallback="False"))
        self.profanity_enabled = ctk.StringVar(value=self.config.get("settings", "profanity_enabled", fallback="False"))
        self.voice_var = ctk.StringVar(value=self.config.get("settings", "VOICE", fallback="th-TH-PremwadeeNeural"))

    def update_topology_stats(self):
        ex = self.opt_config["Settings"].getboolean("exclude_core_0", fallback=True)
        smt = self.opt_config["Settings"].getboolean("disable_smt", fallback=False)
        p, e = split_p_e_cores(ex, smt)
        self.pcore_lbl.configure(text=str(len(p)))
        self.ecore_lbl.configure(text=str(len(e)))

    def toggle_tts(self):
        """Thread-safe toggle for Chat-TTS service."""
        if self.btn_toggle_tts.cget("state") == "disabled": return
        
        self.btn_toggle_tts.configure(state="disabled")
        def _task():
            try:
                if not self.engine.is_running:
                    self.save_chat_settings()
                    conf = {
                        "yt_enabled": self.yt_enabled.get(), "yt_id": self.entry_yt.get(),
                        "tw_enabled": self.tw_enabled.get(), "tw_channel": self.entry_tw.get(),
                        "tk_enabled": self.tk_enabled.get(), "tk_username": self.entry_tk.get(),
                        "voice": self.voice_var.get(), "delay_per_char": self.entry_delay_char.get(),
                        "max_delay": self.entry_max_delay.get(), "auto_translate": self.auto_translate.get(),
                        "profanity_enabled": self.profanity_enabled.get()
                    }
                    self.engine.start(conf)
                    self.after(0, lambda: self.btn_toggle_tts.configure(text="STOP CHAT-TTS", fg_color="#dc3545", state="normal"))
                    self.after(0, lambda: self.status_label.configure(text="RUNNING", text_color="#28a745"))
                else:
                    self.engine.stop()
                    self.after(0, lambda: self.btn_toggle_tts.configure(text="START CHAT-TTS", fg_color="#28a745", state="normal"))
                    if not self.opt_running:
                        self.after(0, lambda: self.status_label.configure(text="IDLE", text_color="#ABB2BF"))
            except Exception as e:
                logger.error(f"TTS Toggle Error: {e}")
                self.after(0, lambda: self.btn_toggle_tts.configure(state="normal"))
        
        threading.Thread(target=_task, daemon=True).start()

    def toggle_optimizer(self):
        """Thread-safe toggle for Optimizer service."""
        if self.btn_toggle_opt.cget("state") == "disabled": return

        self.btn_toggle_opt.configure(state="disabled")
        def _task():
            try:
                if not self.opt_running:
                    logger.info("Starting Optimizer Service...")
                    self.opt_stop_event.clear()
                    self.opt_running = True
                    threading.Thread(target=self._run_opt_service, daemon=True).start()
                    self.after(0, lambda: self.btn_toggle_opt.configure(text="STOP OPTIMIZER", fg_color="#dc3545", state="normal"))
                    self.after(0, lambda: self.status_label.configure(text="RUNNING", text_color="#28a745"))
                else:
                    logger.info("Stopping Optimizer Service...")
                    self.opt_stop_event.set()
                    self.opt_running = False
                    self.after(0, lambda: self.btn_toggle_opt.configure(text="START OPTIMIZER", fg_color="#17a2b8", state="normal"))
                    if not self.engine.is_running:
                        self.after(0, lambda: self.status_label.configure(text="IDLE", text_color="#ABB2BF"))
            except Exception as e:
                logger.error(f"Optimizer Toggle Error: {e}")
                self.after(0, lambda: self.btn_toggle_opt.configure(state="normal"))

        threading.Thread(target=_task, daemon=True).start()

    def _run_opt_service(self):
        try: optimize_processes(self.opt_stop_event, 5.0, log_callback=lambda m: logger.info(f"[OPT] {m}"))
        except Exception as e: logger.error(f"Optimizer error: {e}")

    def save_chat_settings(self):
        if not self.config.has_section("settings"): self.config.add_section("settings")
        self.config.set("settings", "yt_enabled", self.yt_enabled.get())
        self.config.set("settings", "tw_enabled", self.tw_enabled.get())
        self.config.set("settings", "tk_enabled", self.tk_enabled.get())
        self.config.set("settings", "auto_translate", self.auto_translate.get())
        self.config.set("settings", "profanity_enabled", self.profanity_enabled.get())
        self.config.set("settings", "YOUTUBE_VIDEO_ID", self.entry_yt.get())
        self.config.set("settings", "tw_channel", self.entry_tw.get())
        self.config.set("settings", "tk_username", self.entry_tk.get())
        self.config.set("settings", "VOICE", self.voice_var.get())
        self.config.set("settings", "delay_per_char", self.entry_delay_char.get())
        self.config.set("settings", "max_delay", self.entry_max_delay.get())
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: self.config.write(f)

    def save_opt_settings(self):
        self.opt_config["Settings"]["exclude_core_0"] = str(self.opt_exclude_c0.get()).lower()
        self.opt_config["Settings"]["disable_smt"] = str(self.opt_disable_smt.get()).lower()
        self.opt_config["Settings"]["auto_cleanup"] = str(self.opt_auto_clean.get()).lower()
        self.opt_config["Settings"]["cleanup_interval"] = str(self.opt_clean_interval.get())
        save_opt_config(self.opt_config); self.update_topology_stats()

    def refresh_opt_list(self):
        for w in self.g_scroll.winfo_children(): w.destroy()
        for name, prio in get_opt_targets(self.opt_config):
            r = ctk.CTkFrame(self.g_scroll, fg_color="#2D2D2D", corner_radius=8)
            r.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(r, text=f"{name} ({prio})", font=("Helvetica", 11, "bold")).pack(side="left", padx=10)
            ctk.CTkButton(r, text="X", width=30, fg_color="#dc3545", command=lambda n=name: self.remove_opt_target(n)).pack(side="right", padx=5)

    def add_opt_target(self):
        n = self.entry_new_game.get().strip()
        if n:
            self.opt_config["Targets"][n] = self.opt_prio_menu.get()
            self.entry_new_game.delete(0, 'end'); self.save_opt_settings(); self.refresh_opt_list()

    def remove_opt_target(self, name):
        self.opt_config.remove_option("Targets", name); self.save_opt_settings(); self.refresh_opt_list()

    def add_opt_path(self):
        f = filedialog.askdirectory()
        if f:
            if "Paths" not in self.opt_config: self.opt_config["Paths"] = {}
            self.opt_config["Paths"][f] = "P-CORE"; self.save_opt_settings()

    def run_junk_cleanup(self):
        def _target():
            self.clean_log.insert("end", "[*] Starting cleanup...\n")
            files, bytes_saved = clean_junk(lambda m: self.clean_log.insert("end", f"{m}\n") or self.clean_log.see("end"))
            self.clean_log.insert("end", f"\n[SUCCESS] Recovered {bytes_saved/(1024*1024):.2f} MB\n")
        threading.Thread(target=_target, daemon=True).start()

    # --- System Tray ---
    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(40, 167, 69))
        menu = (item('Open Suite', self.show_from_tray, default=True), item('Exit', self.exit_app))
        self.tray_icon = pystray.Icon("StreamerSuite", image, "TDitbam Streamer Suite", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def withdraw_to_tray(self): self.withdraw()
    def show_from_tray(self, icon=None, item=None): self.after(0, self.deiconify)
    def exit_app(self, icon=None, item=None): self.tray_icon.stop(); self.quit(); sys.exit(0)

    def on_closing(self): self.withdraw_to_tray()

def run_cli():
    print("[*] Optimizing processes with CorePriority (CLI Mode)...")
    from optimizer_core.optimizer_engine import optimize_processes
    try:
        optimize_processes(None, 3.0, log_callback=lambda m: print(f"[OPT] {m}"))
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
    except Exception as e:
        print(f"\n[!] Critical error: {e}")

def main():
    logger.info("Launching Streamer Suite GUI...")
    app = StreamerSuiteApp()
    app.mainloop()

if __name__ == "__main__":
    # Administrator Elevation Logic for Windows
    if os.name == 'nt':
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("[*] Requesting Administrator privileges...")
            executable = sys.executable
            if getattr(sys, 'frozen', False):
                params = ' '.join(sys.argv[1:])
            else:
                params = f'"{os.path.abspath(sys.argv[0])}" ' + ' '.join(sys.argv[1:])
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
            except Exception as e:
                print(f"[!] Failed to elevate: {e}")
            sys.exit(0)

    try:
        if "--cli" in sys.argv:
            run_cli()
        else:
            main()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
    except Exception as e:
        print(f"\n[!] Critical error: {e}")
