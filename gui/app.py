import customtkinter as ctk
import configparser
import threading
import os
import sys
import logging
import queue
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
from .i18n import THAI, LANGUAGE_NAMES

class GuiLogHandler(logging.Handler):
    def __init__(self, text_widgets):
        super().__init__()
        self.text_widgets = text_widgets
        self.text_widget = text_widgets["all"]
        self.pending = queue.SimpleQueue()
        self.flush_scheduled = False
        self.schedule_lock = threading.Lock()

    def emit(self, record):
        self.pending.put((self._category_for(record), self.format(record)))
        with self.schedule_lock:
            if self.flush_scheduled:
                return
            self.flush_scheduled = True
        try:
            self.text_widget.after(100, self._flush)
        except Exception:
            with self.schedule_lock:
                self.flush_scheduled = False

    @staticmethod
    def _category_for(record):
        """Route a record to one focused tab while All Logs keeps everything."""
        logger_name = record.name.lower()
        message = record.getMessage().lower()

        if any(component in logger_name for component in ("engine", "youtube", "twitch", "tiktok")):
            return "chat"
        if any(term in message for term in ("bot live chat", "tts", "real-time configuration")):
            return "chat"
        if any(term in message for term in ("[opt]", "optimizer", "cleanup", "junk", "core", "auto-shutdown")):
            return "optimizer"
        return None

    @staticmethod
    def _append_messages(text_widget, messages):
        if not messages:
            return
        text_widget.configure(state="normal")
        text_widget.insert("end", "\n".join(messages) + "\n")
        # Bound each tab so long-running services do not make redraws slower.
        line_count = int(text_widget.index("end-1c").split(".")[0])
        if line_count > 3000:
            text_widget.delete("1.0", f"{line_count - 2500}.0")
        text_widget.see("end")
        text_widget.configure(state="disabled")

    def _flush(self):
        messages = []
        while len(messages) < 200:
            try:
                messages.append(self.pending.get_nowait())
            except queue.Empty:
                break
        try:
            if messages:
                batches = {key: [] for key in self.text_widgets}
                for category, message in messages:
                    batches["all"].append(message)
                    if category in batches and category != "all":
                        batches[category].append(message)
                for key, text_widget in self.text_widgets.items():
                    self._append_messages(text_widget, batches[key])
        except Exception:
            pass
        finally:
            with self.schedule_lock:
                self.flush_scheduled = False
            if not self.pending.empty():
                with self.schedule_lock:
                    self.flush_scheduled = True
                try:
                    self.text_widget.after(100, self._flush)
                except Exception:
                    with self.schedule_lock:
                        self.flush_scheduled = False

class App(ctk.CTk):
    def __init__(self, engine, instance_guard=None):
        super().__init__()
        self.title("Streamer Suite")
        self.geometry("1100x800")
        self.instance_guard = instance_guard

        self.icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icon.ico"))
        if os.path.exists(self.icon_path):
            try:
                self.iconbitmap(self.icon_path)
            except Exception:
                pass
        
        self.engine = engine
        self.logger = get_logger("App")
        
        # Load Configs
        self.config = configparser.ConfigParser()
        if os.path.exists(get_config_path()):
            self.config.read(get_config_path(), encoding="utf-8")
        self.language_code = self.config.get("settings", "language", fallback="en-US")
        if self.language_code not in LANGUAGE_NAMES:
            self.language_code = "en-US"
        
        self.opt_config = load_opt_config()
        self.opt_running = False
        self.opt_stop_event = threading.Event()
        self.cpu_monitor_stop_event = threading.Event()
        
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
        
        # Variables for Bot Live Chat
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
        self.voice_provider = ctk.StringVar(value=self.config.get(s, "voice_provider", fallback="edge"))
        self.gtts_language = ctk.StringVar(value=self.config.get(s, "gtts_language", fallback="th"))
        self.gemini_api_key = ctk.StringVar(value=self.config.get(s, "gemini_api_key", fallback=""))
        self.gemini_model = ctk.StringVar(value=self.config.get(s, "gemini_model", fallback="gemini-3.1-flash-tts-preview"))
        self.gemini_voice = ctk.StringVar(value=self.config.get(s, "gemini_voice", fallback="Kore"))
        self.gemini_style = ctk.StringVar(value=self.config.get(s, "gemini_style", fallback="Read the transcript naturally and clearly."))
        self.openai_api_key = ctk.StringVar(value=self.config.get(s, "openai_api_key", fallback=""))
        self.openai_model = ctk.StringVar(value=self.config.get(s, "openai_model", fallback="tts-1"))
        self.openai_voice = ctk.StringVar(value=self.config.get(s, "openai_voice", fallback="alloy"))
        self.openai_instructions = ctk.StringVar(value=self.config.get(s, "openai_instructions", fallback="Speak naturally and clearly."))
        self.openai_speed = ctk.StringVar(value=self.config.get(s, "openai_speed", fallback="1.0"))
        
        # General App Settings
        self.start_minimized = ctk.BooleanVar(value=self.config.getboolean(s, "start_minimized", fallback=False))
        self.run_on_startup = ctk.BooleanVar(value=self.config.getboolean(s, "run_on_startup", fallback=False))
        self.auto_start_optimizer = ctk.BooleanVar(value=self.config.getboolean(s, "auto_start_optimizer", fallback=False))
        self.windows_notifications = ctk.BooleanVar(value=self.config.getboolean(s, "windows_notifications", fallback=True))
        
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
        self.log_handler = GuiLogHandler(self.frames["dashboard"].log_boxes)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))
        base_logger.addHandler(self.log_handler)
        
        # CPU monitoring runs outside Tk's UI thread.
        self.logic.start_cpu_monitor()
        
        self._setup_listeners()
        self._setup_shortcut_handler()
        self.show_frame("dashboard")
        self.apply_language()

        # Start only after every frame and control has been initialized.
        if self.auto_start_optimizer.get():
            self.after(800, self.logic.start_optimizer_automatically)
        if self.instance_guard:
            self.after(250, self._poll_activation_request)
        self.after(1500, lambda: self.notify_windows("Streamer Suite", self.tr("Application is ready")))
        
        # Auto-minimize to system tray if configured
        if self.start_minimized.get():
            self.after(200, self.withdraw_to_tray)

    def _setup_listeners(self):
        """Setup listeners for real-time config updates."""
        for var in [
            self.auto_translate, self.profanity_enabled, self.voice_var,
            self.voice_provider, self.gtts_language, self.gemini_api_key,
            self.gemini_model, self.gemini_voice, self.gemini_style,
            self.openai_api_key, self.openai_model, self.openai_voice,
            self.openai_instructions, self.openai_speed,
        ]:
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
                    # Tk's widget class binding has already handled a regular
                    # Ctrl+V before this additive global binding runs. Only
                    # synthesize Paste when the active keyboard layout gives
                    # the physical V key a different keysym.
                    if str(event.keysym).lower() == "v":
                        return
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

    def tr(self, text):
        """Translate a UI string while preserving an optional emoji prefix."""
        if self.language_code == "th":
            for english, thai in THAI.items():
                if text == english or text.endswith(english):
                    return text[:-len(english)] + thai
            return text

        for english, thai in THAI.items():
            if text == thai or text.endswith(thai):
                return text[:-len(thai)] + english
        return text

    def set_language(self, display_name):
        """Persist and immediately apply the selected UI language."""
        code = next((key for key, name in LANGUAGE_NAMES.items() if name == display_name), "en-US")
        if code == self.language_code:
            return
        self.language_code = code
        if not self.config.has_section("settings"):
            self.config.add_section("settings")
        self.config.set("settings", "language", code)
        with open(get_config_path(), "w", encoding="utf-8") as config_file:
            self.config.write(config_file)
        self.apply_language()

    def apply_language(self):
        """Update existing widgets in-place; no application restart required."""
        def update_tree(widget):
            for option in ("text", "placeholder_text"):
                try:
                    current = widget.cget(option)
                    if isinstance(current, str) and current:
                        translated = self.tr(current)
                        if translated != current:
                            widget.configure(**{option: translated})
                except Exception:
                    pass
            for child in widget.winfo_children():
                update_tree(child)

        update_tree(self)
        dashboard = self.frames.get("dashboard")
        if dashboard is not None:
            dashboard.apply_language()

    # --- System Tray Methods ---
    def create_tray_icon(self):
        icon_path = self.icon_path
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
        else:
            image = Image.new('RGB', (64, 64), color=(40, 167, 69))
            
        menu = (item('Open Streamer Suite', self.show_from_tray, default=True),
                item('Exit', self.exit_app))
        self.tray_icon = pystray.Icon("StreamerSuite", image, "Streamer Suite", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _poll_activation_request(self):
        """Restore the existing window when the user launches the app again."""
        if self.instance_guard and self.instance_guard.activation_requested():
            self.show_from_tray()
        self.after(250, self._poll_activation_request)

    def notify_windows(self, title, message):
        """Show a native tray notification using the application's icon."""
        if not self.windows_notifications.get() or not hasattr(self, "tray_icon"):
            return
        try:
            self.tray_icon.notify(message, title)
        except Exception as error:
            self.logger.debug(f"Windows notification unavailable: {error}")

    def withdraw_to_tray(self):
        self.withdraw()

    def show_from_tray(self, icon=None, item=None):
        def restore_window():
            self.deiconify()
            self.state("normal")
            self.lift()
            # A short topmost pulse reliably brings the existing window to
            # the foreground after a duplicate launch, then restores normal
            # window behavior.
            self.attributes("-topmost", True)
            self.after(150, lambda: self.attributes("-topmost", False))
            self.focus_force()

        self.after(0, restore_window)

    def exit_app(self, icon=None, item=None):
        self.logger.info("Exiting application...")
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.engine.stop()
        self.opt_stop_event.set()
        self.cpu_monitor_stop_event.set()
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
    def add_selected_process(self): self.logic.add_selected_process()
    def refresh_running_processes(self): self.logic.refresh_running_processes()
    def filter_running_processes(self): self.logic.filter_running_processes()
    def browse_opt_target(self): self.logic.browse_opt_target()
    def remove_opt_target(self, name): self.logic.remove_opt_target(name)
    def add_opt_path(self): self.logic.add_opt_path()
    def remove_opt_path(self, path): self.logic.remove_opt_path(path)
    def run_junk_cleanup(self): self.logic.run_junk_cleanup()
    def update_topology_stats(self): self.logic.update_topology_stats()

    def run(self):
        self.mainloop()
