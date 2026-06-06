import customtkinter as ctk
import os
import sys
import threading
import logging
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

    def toggle_tts(self):
        if self.app.frames["dashboard"].btn_toggle_tts.cget("state") == "disabled": return
        self.app.frames["dashboard"].btn_toggle_tts.configure(state="disabled")
        
        def _task():
            try:
                if not self.app.engine.is_running:
                    self.logger.info("Starting Chat-TTS System...")
                    self.save_chat_settings()
                    conf = {
                        "yt_enabled": self.app.yt_enabled.get(), "yt_id": self.app.entry_yt.get(),
                        "tw_enabled": self.app.tw_enabled.get(), "tw_channel": self.app.entry_tw.get(),
                        "tk_enabled": self.app.tk_enabled.get(), "tk_username": self.app.entry_tk.get(),
                        "voice": self.app.voice_var.get(), "delay_per_char": self.app.entry_delay_char.get(),
                        "max_delay": self.app.entry_max_delay.get(), "auto_translate": self.app.auto_translate.get(),
                        "profanity_enabled": self.app.profanity_enabled.get()
                    }
                    self.app.engine.start(conf)
                    self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_tts.configure(text="STOP CHAT-TTS", fg_color="#dc3545", state="normal"))
                    self.app.after(0, lambda: self.app.frames["dashboard"].status_label.configure(text="RUNNING", text_color="#28a745"))
                else:
                    self.logger.info("Stopping Chat-TTS System...")
                    self.app.engine.stop()
                    self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_tts.configure(text="START CHAT-TTS", fg_color="#28a745", state="normal"))
                    if not self.app.opt_running:
                        self.app.after(0, lambda: self.app.frames["dashboard"].status_label.configure(text="IDLE", text_color="#ABB2BF"))
            except Exception as e:
                self.logger.error(f"TTS Toggle Error: {e}")
                self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_tts.configure(state="normal"))
        
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
                    self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_opt.configure(text="STOP OPTIMIZER", fg_color="#dc3545", state="normal"))
                    self.app.after(0, lambda: self.app.frames["dashboard"].status_label.configure(text="RUNNING", text_color="#28a745"))
                else:
                    self.logger.info("Stopping Optimizer Service...")
                    self.app.opt_stop_event.set()
                    self.app.opt_running = False
                    self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_opt.configure(text="START OPTIMIZER", fg_color="#17a2b8", state="normal"))
                    if not self.app.engine.is_running:
                        self.app.after(0, lambda: self.app.frames["dashboard"].status_label.configure(text="IDLE", text_color="#ABB2BF"))
            except Exception as e:
                self.logger.error(f"Optimizer Toggle Error: {e}")
                self.app.after(0, lambda: self.app.frames["dashboard"].btn_toggle_opt.configure(state="normal"))
        
        threading.Thread(target=_task, daemon=True).start()

    def _run_opt_service(self):
        try: 
            optimize_processes(self.app.opt_stop_event, 5.0, log_callback=lambda m: self.logger.info(f"[OPT] {m}"))
        except Exception as e: 
            self.logger.error(f"Optimizer error: {e}")

    def save_chat_settings(self):
        if not self.app.config.has_section("tts"): self.app.config.add_section("tts")
        self.app.config.set("tts", "yt_enabled", self.app.yt_enabled.get())
        self.app.config.set("tts", "tw_enabled", self.app.tw_enabled.get())
        self.app.config.set("tts", "tk_enabled", self.app.tk_enabled.get())
        self.app.config.set("tts", "auto_translate", self.app.auto_translate.get())
        self.app.config.set("tts", "profanity_enabled", self.app.profanity_enabled.get())
        self.app.config.set("tts", "youtube_video_id", self.app.entry_yt.get())
        self.app.config.set("tts", "tw_channel", self.app.entry_tw.get())
        self.app.config.set("tts", "tk_username", self.app.entry_tk.get())
        self.app.config.set("tts", "voice", self.app.voice_var.get())
        self.app.config.set("tts", "delay_per_char", self.app.entry_delay_char.get())
        self.app.config.set("tts", "max_delay", self.app.entry_max_delay.get())
        
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
            self.app.engine.update_config({
                "voice": self.app.voice_var.get(), 
                "delay_per_char": self.app.entry_delay_char.get(), 
                "max_delay": self.app.entry_max_delay.get(), 
                "auto_translate": self.app.auto_translate.get(), 
                "profanity_enabled": self.app.profanity_enabled.get()
            })
        self.logger.info("Chat-TTS Settings Saved Successfully")

    def save_opt_settings(self):
        self.app.opt_config["Settings"]["exclude_core_0"] = str(self.app.opt_exclude_c0.get()).lower()
        self.app.opt_config["Settings"]["disable_smt"] = str(self.app.opt_disable_smt.get()).lower()
        self.app.opt_config["Settings"]["auto_cleanup"] = str(self.app.opt_auto_clean.get()).lower()
        self.app.opt_config["Settings"]["cleanup_interval"] = str(self.app.opt_clean_interval.get())
        save_opt_config(self.app.opt_config)
        self.update_topology_stats()

    def update_topology_stats(self):
        ex = self.app.opt_exclude_c0.get()
        smt = self.app.opt_disable_smt.get()
        p, e = split_p_e_cores(ex, smt)
        self.app.frames["dashboard"].pcore_lbl.configure(text=str(len(p)))
        self.app.frames["dashboard"].ecore_lbl.configure(text=str(len(e)))

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
            self.app.opt_config["targets"][n] = self.app.opt_prio_menu.get()
            self.app.entry_new_game.delete(0, 'end')
            self.save_opt_settings()
            self.refresh_opt_list()

    def remove_opt_target(self, name):
        self.app.opt_config.remove_option("targets", name)
        self.save_opt_settings()
        self.refresh_opt_list()

    def add_opt_path(self):
        f = filedialog.askdirectory()
        if f:
            if "paths" not in self.app.opt_config: self.app.opt_config["paths"] = {}
            self.app.opt_config["paths"][f] = "P-CORE"
            self.save_opt_settings()
            self.refresh_path_list()

    def remove_opt_path(self, path):
        self.app.opt_config.remove_option("paths", path)
        self.save_opt_settings()
        self.refresh_path_list()

    def run(self):
        self.app.mainloop()
