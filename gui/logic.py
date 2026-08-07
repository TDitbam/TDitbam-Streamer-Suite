import customtkinter as ctk
import os
import sys
import threading
import logging
import psutil
from tkinter import filedialog
from core.app_logger import get_app_dir, get_logger, get_config_path
from optimizer.optimizer_core.config_loader import save_config as save_opt_config, get_targets as get_opt_targets, get_paths as get_opt_paths
from optimizer.optimizer_core.optimizer_engine import optimize_processes
from optimizer.optimizer_core.cleaner import clean_junk
from optimizer.optimizer_core.cpu_topology import split_p_e_cores

class AppLogic:
    def __init__(self, app, engine):
        self.app = app
        self.engine = engine
        self.logger = get_logger("Logic")
        self._cpu_monitor_thread = None
        self._optimizer_p_core_count = 0
        self._optimizer_e_core_count = 0
        self._topology_refresh_id = 0
        self._process_refresh_running = False
        self._running_process_names = []
        self._process_refresh_after_id = None

    def toggle_tts(self):
        btn_dash = self.app.frames["dashboard"].btn_toggle_tts
        btn_chat = self.app.btn_toggle_tts_chat
        
        if btn_dash.cget("state") == "disabled": return

        if not self.app.engine.is_running:
            # A new chat session gets a clean focused tab; All Logs remains a
            # complete application history.
            self.app.frames["dashboard"].clear_log("chat")
        
        btn_dash.configure(state="disabled")
        btn_chat.configure(state="disabled")
        
        def _task():
            try:
                if not self.app.engine.is_running:
                    self.logger.info("Starting Bot Live Chat...")
                    # 1. Save current UI to disk
                    self.save_chat_settings()
                    
                    # 2. Build config dict from the fresh app state (already updated by save_chat_settings)
                    s = "settings"
                    conf = {
                        "yt_enabled": self.app.config.get(s, "yt_enabled", fallback="False"),
                        "yt_id": self.app.config.get(s, "yt_video_id", fallback=""),
                        "tw_enabled": self.app.config.get(s, "tw_enabled", fallback="False"),
                        "tw_channel": self.app.config.get(s, "tw_channel", fallback=""),
                        "tk_enabled": self.app.config.get(s, "tk_enabled", fallback="False"),
                        "tk_username": self.app.config.get(s, "tk_username", fallback=""),
                        "voice": self.app.config.get(s, "voice", fallback="th-TH-PremwadeeNeural"),
                        "voice_provider": self.app.config.get(s, "voice_provider", fallback="edge"),
                        "gtts_language": self.app.config.get(s, "gtts_language", fallback="th"),
                        "gemini_api_key": self.app.config.get(s, "gemini_api_key", fallback=""),
                        "gemini_model": self.app.config.get(s, "gemini_model", fallback="gemini-3.1-flash-tts-preview"),
                        "gemini_voice": self.app.config.get(s, "gemini_voice", fallback="Kore"),
                        "gemini_style": self.app.config.get(s, "gemini_style", fallback="Read the transcript naturally and clearly."),
                        "openai_api_key": self.app.config.get(s, "openai_api_key", fallback=""),
                        "openai_model": self.app.config.get(s, "openai_model", fallback="tts-1"),
                        "openai_voice": self.app.config.get(s, "openai_voice", fallback="alloy"),
                        "openai_instructions": self.app.config.get(s, "openai_instructions", fallback="Speak naturally and clearly."),
                        "openai_speed": self.app.config.get(s, "openai_speed", fallback="1.0"),
                        "delay_per_char": self.app.config.get(s, "delay_per_char", fallback="0.03"),
                        "max_delay": self.app.config.get(s, "max_delay", fallback="2.0"),
                        "auto_translate": self.app.config.get(s, "auto_translate", fallback="False"),
                        "profanity_enabled": self.app.config.get(s, "profanity_enabled", fallback="False")
                    }
                    
                    self.app.engine.start(conf)
                    
                    def _update_ui_start():
                        btn_dash.configure(text=self.app.tr("STOP BOT LIVE CHAT"), fg_color="#dc3545", state="normal")
                        btn_chat.configure(text=self.app.tr("STOP BOT LIVE CHAT"), fg_color="#dc3545", state="normal")
                        self.app.frames["dashboard"].status_label.configure(text=self.app.tr("RUNNING"), text_color="#28a745")
                        self.app.notify_windows("Bot Live Chat", self.app.tr("Bot Live Chat started"))
                    
                    self.app.after(0, _update_ui_start)
                else:
                    self.logger.info("Stopping Bot Live Chat...")
                    self.app.engine.stop()
                    
                    def _update_ui_stop():
                        btn_dash.configure(text=self.app.tr("START BOT LIVE CHAT"), fg_color="#28a745", state="normal")
                        btn_chat.configure(text=self.app.tr("START BOT LIVE CHAT"), fg_color="#28a745", state="normal")
                        if not self.app.opt_running:
                            self.app.frames["dashboard"].status_label.configure(text=self.app.tr("IDLE"), text_color="#ABB2BF")
                        self.app.notify_windows("Bot Live Chat", self.app.tr("Bot Live Chat stopped"))
                    
                    self.app.after(0, _update_ui_stop)
            except Exception as e:
                self.logger.error(f"TTS Toggle Error: {e}")
                self.app.after(0, lambda: (btn_dash.configure(state="normal"), btn_chat.configure(state="normal")))
        
        threading.Thread(target=_task, daemon=True).start()

    def toggle_optimizer(self):
        if self.app.frames["dashboard"].btn_toggle_opt.cget("state") == "disabled": return
        self.app.frames["dashboard"].btn_toggle_opt.configure(state="disabled")
        
        def _task():
            try:
                if not self.app.opt_running:
                    self.logger.info("Starting Optimizer Service...")
                    self.app.opt_stop_event.clear()
                    self.app.opt_running = True
                    threading.Thread(target=self._run_opt_service, daemon=True).start()
                    self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_opt.configure(text=self.app.tr("STOP OPTIMIZER"), fg_color="#dc3545", state="normal"))
                    self.app.after(0, lambda: self.app.frames["dashboard"].status_label.configure(text=self.app.tr("RUNNING"), text_color="#28a745"))
                    self.app.after(0, lambda: self.app.notify_windows("Optimizer", self.app.tr("Optimizer started")))
                else:
                    self.logger.info("Stopping Optimizer Service...")
                    self.app.opt_stop_event.set()
                    self.app.opt_running = False
                    self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_opt.configure(text=self.app.tr("START OPTIMIZER"), fg_color="#17a2b8", state="normal"))
                    if not self.app.engine.is_running:
                        self.app.after(0, lambda: self.app.frames["dashboard"].status_label.configure(text=self.app.tr("IDLE"), text_color="#ABB2BF"))
                    self.app.after(0, lambda: self.app.notify_windows("Optimizer", self.app.tr("Optimizer stopped")))
            except Exception as e:
                self.logger.error(f"Optimizer Toggle Error: {e}")
                self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_opt.configure(state="normal"))
        
        threading.Thread(target=_task, daemon=True).start()

    def start_optimizer_automatically(self):
        """Start Optimizer once after launch when enabled in App Settings."""
        if self.app.opt_running or not self.app.auto_start_optimizer.get():
            return
        self.logger.info("Auto Start Optimizer enabled; starting service...")
        self.toggle_optimizer()

    def _run_opt_service(self):
        try: 
            optimize_processes(self.app.opt_stop_event, 5.0, log_callback=lambda m: self.logger.info(f"[OPT] {m}"))
        except Exception as e: 
            self.logger.error(f"Optimizer error: {e}")

    def save_chat_settings(self):
        """Save current GUI state to config.ini with standardized lowercase keys."""
        if not self.app.config.has_section("settings"): self.app.config.add_section("settings")
        s = "settings"
        self.app.config.set(s, "yt_enabled", self.app.yt_enabled.get())
        self.app.config.set(s, "tw_enabled", self.app.tw_enabled.get())
        self.app.config.set(s, "tk_enabled", self.app.tk_enabled.get())
        self.app.config.set(s, "auto_translate", self.app.auto_translate.get())
        self.app.config.set(s, "profanity_enabled", self.app.profanity_enabled.get())
        
        # Standardized lowercase keys
        self.app.config.set(s, "yt_video_id", self.app.entry_yt.get())
        self.app.config.set(s, "tw_channel", self.app.entry_tw.get())
        self.app.config.set(s, "tk_username", self.app.entry_tk.get())
        self.app.config.set(s, "voice", self.app.voice_var.get())
        self.app.config.set(s, "voice_provider", self.app.voice_provider.get())
        self.app.config.set(s, "gtts_language", self.app.gtts_language.get())
        self.app.config.set(s, "gemini_api_key", self.app.gemini_api_key.get())
        self.app.config.set(s, "gemini_model", self.app.gemini_model.get())
        self.app.config.set(s, "gemini_voice", self.app.gemini_voice.get())
        self.app.config.set(s, "gemini_style", self.app.gemini_style.get())
        self.app.config.set(s, "openai_api_key", self.app.openai_api_key.get())
        self.app.config.set(s, "openai_model", self.app.openai_model.get())
        self.app.config.set(s, "openai_voice", self.app.openai_voice.get())
        self.app.config.set(s, "openai_instructions", self.app.openai_instructions.get())
        self.app.config.set(s, "openai_speed", self.app.openai_speed.get())
        self.app.config.set(s, "delay_per_char", self.app.entry_delay_char.get())
        self.app.config.set(s, "max_delay", self.app.entry_max_delay.get())
        
        # Backward compatibility / Clean up old keys
        for old_key in ["youtube_video_id", "VOICE", "YOUTUBE_VIDEO_ID"]:
            if self.app.config.has_option(s, old_key):
                self.app.config.remove_option(s, old_key)
        
        # Remove old [tts] section if it exists
        if self.app.config.has_section("tts"):
            self.app.config.remove_section("tts")

        with open(get_config_path(), "w", encoding="utf-8") as f: 
            self.app.config.write(f)
            
        prof_file = os.path.join(get_app_dir(), "resources", "bad_words.txt") if not getattr(sys, 'frozen', False) else os.path.join(get_app_dir(), "bad_words.txt")
        # Ensure resources dir exists
        res_dir = os.path.dirname(prof_file)
        if not os.path.exists(res_dir): os.makedirs(res_dir)
        
        try:
            with open(prof_file, "w", encoding="utf-8") as f: 
                f.write(self.app.textbox_filter.get("1.0", "end-1c"))
        except: pass
        
        if self.app.engine.is_running:
            self.app.logic.apply_realtime_config()
            
        self.logger.info("Bot Live Chat settings saved successfully")

    def apply_realtime_config(self):
        """Apply current GUI settings to the engine in real-time."""
        if self.app.engine.is_running:
            conf = {
                "voice": self.app.voice_var.get(),
                "voice_provider": self.app.voice_provider.get(),
                "gtts_language": self.app.gtts_language.get(),
                "gemini_api_key": self.app.gemini_api_key.get(),
                "gemini_model": self.app.gemini_model.get(),
                "gemini_voice": self.app.gemini_voice.get(),
                "gemini_style": self.app.gemini_style.get(),
                "openai_api_key": self.app.openai_api_key.get(),
                "openai_model": self.app.openai_model.get(),
                "openai_voice": self.app.openai_voice.get(),
                "openai_instructions": self.app.openai_instructions.get(),
                "openai_speed": self.app.openai_speed.get(),
                "delay_per_char": self.app.entry_delay_char.get(),
                "max_delay": self.app.entry_max_delay.get(),
                "auto_translate": self.app.auto_translate.get(),
                "profanity_enabled": self.app.profanity_enabled.get()
            }
            self.app.engine.update_config(conf)
            self.logger.info("Real-time configuration applied.")

    def save_opt_settings(self):
        self.app.opt_config["Settings"]["exclude_core_0"] = str(self.app.opt_exclude_c0.get()).lower()
        self.app.opt_config["Settings"]["disable_smt"] = str(self.app.opt_disable_smt.get()).lower()
        self.app.opt_config["Settings"]["auto_cleanup"] = str(self.app.opt_auto_clean.get()).lower()
        self.app.opt_config["Settings"]["cleanup_interval"] = str(self.app.opt_clean_interval.get())
        self.app.opt_config["Settings"]["auto_shutdown"] = str(self.app.opt_auto_shutdown.get()).lower()
        self.app.opt_config["Settings"]["shutdown_time"] = str(self.app.opt_shutdown_time.get())
        
        save_opt_config(self.app.opt_config)
        self.sync_shutdown_task()
        self.update_topology_stats()

    def sync_shutdown_task(self):
        """Sync the auto-shutdown task with Windows Task Scheduler."""
        if os.name != 'nt': return
        
        import subprocess
        task_name = "TDitbam_AutoShutdown"
        enabled = self.app.opt_auto_shutdown.get()
        time_str = self.app.opt_shutdown_time.get().strip()
        
        # Flags to hide console window
        CREATE_NO_WINDOW = 0x08000000
        
        # 1. Always try to delete existing task first to ensure clean state
        subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                       creationflags=CREATE_NO_WINDOW)
        
        if enabled and time_str:
            # Validate time format HH:mm
            import re
            if re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
                # 2. Create new task
                # /sc daily /st HH:mm (Run daily at specific time)
                # /tr "shutdown /s /f /t 60" (Shutdown with force and 60s delay)
                cmd = ['schtasks', '/create', '/tn', task_name, '/tr', 'shutdown /s /f /t 60', '/sc', 'daily', '/st', time_str, '/f']
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                     creationflags=CREATE_NO_WINDOW)
                
                if res.returncode == 0:
                    self.logger.info(f"Auto-Shutdown scheduled at {time_str} (Daily)")
                else:
                    self.logger.error(f"Failed to schedule task. Error: {res.stderr.strip()}")
            else:
                self.logger.error(f"Invalid shutdown time format: '{time_str}'. Use HH:mm (e.g., 23:30)")
        else:
            self.logger.info("Auto-Shutdown task disabled (or time is empty).")

    def save_app_settings(self):
        s = "settings"
        if not self.app.config.has_section(s):
            self.app.config.add_section(s)
        self.app.config.set(s, "start_minimized", str(self.app.start_minimized.get()))
        self.app.config.set(s, "run_on_startup", str(self.app.run_on_startup.get()))
        self.app.config.set(s, "auto_start_optimizer", str(self.app.auto_start_optimizer.get()))
        self.app.config.set(s, "windows_notifications", str(self.app.windows_notifications.get()))
        
        # Save to config file
        from core.app_logger import get_config_path
        with open(get_config_path(), "w", encoding="utf-8") as f:
            self.app.config.write(f)
            
        self.logger.info("General application settings saved.")
        self.sync_startup_task()

    def sync_startup_task(self):
        """Sync the elevated startup task with Windows Task Scheduler."""
        if os.name != 'nt': return
        
        import subprocess
        import sys
        task_name = "TDitbam_Startup"
        enabled = self.app.run_on_startup.get()
        
        # Flags to hide console window
        CREATE_NO_WINDOW = 0x08000000
        
        # 1. Always try to delete existing task first to ensure clean state
        subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                       creationflags=CREATE_NO_WINDOW)
                       
        if enabled:
            # Determine path to execute
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
                task_run = f'"{app_path}"'
            else:
                app_path = os.path.abspath(sys.argv[0])
                python_exe = sys.executable
                # Use pythonw if possible to avoid displaying terminal window
                if python_exe.endswith("python.exe"):
                    pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
                    if os.path.exists(pythonw_exe):
                        python_exe = pythonw_exe
                task_run = f'"{python_exe}" "{app_path}"'
                
            # Create Task
            # /sc onlogon: run at logon
            # /rl highest: run with administrator/highest privileges (bypasses UAC)
            # /f: force creation (overwrite if exists)
            cmd = ['schtasks', '/create', '/tn', task_name, '/tr', task_run, '/sc', 'onlogon', '/rl', 'highest', '/f']
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                 creationflags=CREATE_NO_WINDOW)
                                 
            if res.returncode == 0:
                self.logger.info("Startup task scheduled successfully with highest privileges (bypassing UAC).")
            else:
                self.logger.error(f"Failed to schedule startup task. Error: {res.stderr.strip()}")

    def start_cpu_monitor(self):
        """Sample per-core CPU usage off the Tk main thread."""
        if self._cpu_monitor_thread and self._cpu_monitor_thread.is_alive():
            return
        self.app.cpu_monitor_stop_event.clear()
        exclude_core_0 = self.app.opt_exclude_c0.get()
        disable_smt = self.app.opt_disable_smt.get()

        def monitor():
            # CPU topology is stable for the lifetime of the process, so do
            # the Windows API query once instead of on every UI refresh.
            p_cores, e_cores = split_p_e_cores(False, False)
            optimizer_p, optimizer_e = split_p_e_cores(exclude_core_0, disable_smt)
            self._optimizer_p_core_count = len(optimizer_p)
            self._optimizer_e_core_count = len(optimizer_e)
            psutil.cpu_percent(interval=None, percpu=True)  # Prime counters.
            while not self.app.cpu_monitor_stop_event.wait(1.0):
                per_cpu = psutil.cpu_percent(interval=None, percpu=True)
                self.app.after(
                    0,
                    lambda p=p_cores, e=e_cores, usage=per_cpu:
                        self._render_cpu_stats(p, e, usage),
                )

        self._cpu_monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._cpu_monitor_thread.start()

    def update_topology_stats(self):
        """Refresh the effective Optimizer pools without blocking Tk."""
        exclude_core_0 = self.app.opt_exclude_c0.get()
        disable_smt = self.app.opt_disable_smt.get()
        self._topology_refresh_id += 1
        refresh_id = self._topology_refresh_id

        def refresh():
            p_cores, e_cores = split_p_e_cores(exclude_core_0, disable_smt)
            if refresh_id != self._topology_refresh_id:
                return
            self._optimizer_p_core_count = len(p_cores)
            self._optimizer_e_core_count = len(e_cores)

        threading.Thread(target=refresh, daemon=True).start()

    def _render_cpu_stats(self, p, e, per_cpu):
        """Render a prepared CPU sample on Tk's UI thread."""

        def average_usage(core_ids):
            values = [per_cpu[index] for index in core_ids if 0 <= index < len(per_cpu)]
            return sum(values) / len(values) if values else None

        p_usage = average_usage(p)
        e_usage = average_usage(e)
        dashboard = self.app.frames["dashboard"]
        dashboard.pcore_lbl.configure(text=f"{p_usage:.0f}%" if p_usage is not None else "N/A")
        dashboard.ecore_lbl.configure(text=f"{e_usage:.0f}%" if e_usage is not None else "N/A")
        optimizer_uses = self.app.tr("Optimizer uses")
        logical_cores = self.app.tr("logical cores")
        optimizer_p_count = self._optimizer_p_core_count if self.app.opt_running else 0
        optimizer_e_count = self._optimizer_e_core_count if self.app.opt_running else 0
        dashboard.pcore_count_lbl.configure(
            text=f"{optimizer_uses} {optimizer_p_count} / {len(p)} {logical_cores}"
        )
        dashboard.ecore_count_lbl.configure(
            text=f"{optimizer_uses} {optimizer_e_count} / {len(e)} {logical_cores}"
        )

    def run_junk_cleanup(self):
        def _target():
            self.app.clean_log.configure(state="normal")
            self.app.clean_log.insert("end", "Starting junk cleanup...\n")
            self.app.clean_log.see("end")
            
            def log_fn(msg):
                self.app.after(0, lambda: (self.app.clean_log.insert("end", f"{msg}\n"), self.app.clean_log.see("end")))
            
            files, bytes_saved = clean_junk(log_fn)
            mb = bytes_saved / (1024 * 1024)
            log_fn(f"--- Cleanup Finished ---")
            log_fn(f"Files deleted: {files}")
            log_fn(f"Space recovered: {mb:.2f} MB")
            self.app.after(0, lambda: self.app.clean_log.configure(state="disabled"))
            self.app.after(0, lambda: self.app.notify_windows(
                self.app.tr("Cleanup"),
                f"{self.app.tr('Cleanup completed')}: {files} files, {mb:.2f} MB",
            ))
            
        threading.Thread(target=_target, daemon=True).start()

    def refresh_opt_list(self):
        for w in self.app.g_scroll.winfo_children(): w.destroy()
        for name, prio in get_opt_targets(self.app.opt_config):
            r = ctk.CTkFrame(self.app.g_scroll, fg_color="#2D2D2D", corner_radius=8)
            r.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(r, text=f"{name} ({prio})", font=self.app.bold_font).pack(side="left", padx=10)
            ctk.CTkButton(r, text="X", width=30, fg_color="#dc3545", command=lambda n=name: self.remove_opt_target(n)).pack(side="right", padx=5)

    def refresh_path_list(self):
        for w in self.app.d_scroll.winfo_children(): w.destroy()
        for path, prio in get_opt_paths(self.app.opt_config):
            r = ctk.CTkFrame(self.app.d_scroll, fg_color="#2D2D2D", corner_radius=8)
            r.pack(fill="x", pady=2, padx=5)
            display_path = (path[:40] + '...') if len(path) > 40 else path
            ctk.CTkLabel(r, text=f"{display_path} ({prio})", font=self.app.bold_font).pack(side="left", padx=10)
            ctk.CTkButton(r, text="X", width=30, fg_color="#dc3545", command=lambda p=path: self.remove_opt_path(p)).pack(side="right", padx=5)

    def add_opt_target(self):
        n = self.app.entry_new_game.get().strip()
        if n:
            self._save_opt_target(n)
            self.app.entry_new_game.delete(0, 'end')

    def _save_opt_target(self, process_name):
        process_name = os.path.basename(process_name.strip())
        if not process_name:
            return
        if "Targets" not in self.app.opt_config:
            self.app.opt_config["Targets"] = {}
        self.app.opt_config["Targets"][process_name] = self.app.opt_priority_var.get()
        self.save_opt_settings()
        self.refresh_opt_list()
        self.app.notify_windows("Optimizer", f"{self.app.tr('Program added')}: {process_name}")

    def add_selected_process(self):
        process_name = self.app.running_process_var.get().strip()
        unavailable = {
            self.app.tr("No running process found"),
            self.app.tr("No matching process"),
        }
        if process_name and process_name not in unavailable:
            self._save_opt_target(process_name)

    def filter_running_processes(self):
        """Filter the cached process list immediately as the user types."""
        query = self.app.process_search_var.get().strip().casefold()
        if query:
            values = [name for name in self._running_process_names if query in name.casefold()]
        else:
            values = list(self._running_process_names)
        if not values:
            placeholder = "No matching process" if query else "No running process found"
            values = [self.app.tr(placeholder)]
        self.app.running_process_menu.configure(values=values)
        self.app.running_process_var.set(values[0])

    def refresh_running_processes(self):
        if self._process_refresh_running:
            return
        if self._process_refresh_after_id:
            try:
                self.app.after_cancel(self._process_refresh_after_id)
            except Exception:
                pass
            self._process_refresh_after_id = None
        self._process_refresh_running = True

        def scan():
            names = set()
            for process in psutil.process_iter(["name"]):
                try:
                    name = (process.info.get("name") or "").strip()
                    if name:
                        names.add(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            values = sorted(names, key=str.casefold)

            def apply_values():
                self._running_process_names = values
                self.filter_running_processes()
                self._process_refresh_running = False
                # Keep the cache fresh automatically; only one timer exists.
                self._process_refresh_after_id = self.app.after(
                    5000, self.refresh_running_processes
                )

            self.app.after(0, apply_values)

        threading.Thread(target=scan, daemon=True).start()

    def browse_opt_target(self):
        path = filedialog.askopenfilename(
            title=self.app.tr("Select a program"),
            filetypes=[("Windows programs", "*.exe"), ("All files", "*.*")],
        )
        if path:
            self.app.entry_new_game.delete(0, "end")
            self.app.entry_new_game.insert(0, os.path.basename(path))

    def remove_opt_target(self, name):
        self.app.opt_config.remove_option("Targets", name)
        self.save_opt_settings()
        self.refresh_opt_list()

    def add_opt_path(self):
        f = filedialog.askdirectory()
        if f:
            if "Paths" not in self.app.opt_config: self.app.opt_config["Paths"] = {}
            prio = self.app.opt_dir_prio_menu.get()
            self.app.opt_config["Paths"][f] = prio
            self.save_opt_settings()
            self.refresh_path_list()

    def remove_opt_path(self, path):
        self.app.opt_config.remove_option("Paths", path)
        self.save_opt_settings()
        self.refresh_path_list()

    def run(self):
        self.app.mainloop()
