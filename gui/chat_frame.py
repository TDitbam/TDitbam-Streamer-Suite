import customtkinter as ctk
import os
import sys
from core.app_logger import get_app_dir

class ChatFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Control Section
        ctrl_f = ctk.CTkFrame(self.scroll, fg_color="#1E1E1E", corner_radius=15)
        ctrl_f.pack(fill="x", pady=(0, 15))
        
        inner_ctrl = ctk.CTkFrame(ctrl_f, fg_color="transparent")
        inner_ctrl.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(inner_ctrl, text="Engine Control", font=self.app.bold_font).pack(side="left")
        
        # We reuse the logic from dashboard
        self.app.btn_toggle_tts_chat = ctk.CTkButton(inner_ctrl, text="START CHAT-TTS", height=45, width=200, 
                                                    fg_color="#28a745", hover_color="#218838", font=self.app.bold_font,
                                                    command=self.app.toggle_tts)
        self.app.btn_toggle_tts_chat.pack(side="right")
        
        # Sections for Platform Config
        for platform, var, entry_attr, placeholder in [
            ("YouTube Live", self.app.yt_enabled, "entry_yt", "Video ID or URL"),
            ("Twitch Chat", self.app.tw_enabled, "entry_tw", "Channel Name"),
            ("TikTok Live", self.app.tk_enabled, "entry_tk", "@username")
        ]:
            f = ctk.CTkFrame(self.scroll, fg_color="#2D2D2D", corner_radius=10)
            f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=platform, font=self.app.bold_font).pack(anchor="w", padx=15, pady=5)
            inner = ctk.CTkFrame(f, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=(0, 10))
            ctk.CTkCheckBox(inner, text="Enabled", variable=var, onvalue="True", offvalue="False", font=self.app.default_font).pack(side="left")
            entry = ctk.CTkEntry(inner, placeholder_text=placeholder, width=350, font=self.app.default_font)
            setattr(self.app, entry_attr, entry)
            
            # Map platform to config key with backward compatibility
            s = "settings"
            tts_old = "tts"
            if platform == "YouTube Live":
                val = self.app.config.get(s, "yt_video_id", fallback=self.app.config.get(tts_old, "youtube_video_id", fallback=self.app.config.get(s, "YOUTUBE_VIDEO_ID", fallback="")))
            elif platform == "Twitch Chat":
                val = self.app.config.get(s, "tw_channel", fallback=self.app.config.get(tts_old, "tw_channel", fallback=""))
            else: # TikTok
                val = self.app.config.get(s, "tk_username", fallback=self.app.config.get(tts_old, "tk_username", fallback=""))
            
            entry.insert(0, val)
            entry.pack(side="right")
            
            from .context_menu import ContextMenu
            ContextMenu.add_context_menu(entry)

        # Voice & General Settings
        v_f = ctk.CTkFrame(self.scroll, fg_color="#2D2D2D", corner_radius=10)
        v_f.pack(fill="x", pady=5)
        
        # First row: Voice and Translate
        row1 = ctk.CTkFrame(v_f, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(row1, text="Voice Model:", font=self.app.default_font).pack(side="left")
        self.voice_menu = ctk.CTkOptionMenu(row1, values=["th-TH-PremwadeeNeural", "th-TH-NiwatNeural"], variable=self.app.voice_var, font=self.app.default_font)
        self.voice_menu.pack(side="left", padx=10)
        ctk.CTkCheckBox(row1, text="Auto-Translate (TH)", variable=self.app.auto_translate, onvalue="True", offvalue="False", font=self.app.default_font).pack(side="left", padx=10)
        ctk.CTkCheckBox(row1, text="Filter Profanity", variable=self.app.profanity_enabled, onvalue="True", offvalue="False", font=self.app.default_font).pack(side="left", padx=10)

        # Second row: Delays
        row2 = ctk.CTkFrame(v_f, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(row2, text="Delay/Char:", font=self.app.default_font).pack(side="left")
        self.app.entry_delay_char = ctk.CTkEntry(row2, width=60, font=self.app.default_font)
        
        s = "settings"
        tts_old = "tts"
        delay_val = self.app.config.get(s, "delay_per_char", fallback=self.app.config.get(tts_old, "delay_per_char", fallback="0.03"))
        self.app.entry_delay_char.insert(0, delay_val)
        self.app.entry_delay_char.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Max Delay:", font=self.app.default_font).pack(side="left", padx=(10, 0))
        self.app.entry_max_delay = ctk.CTkEntry(row2, width=60, font=self.app.default_font)
        max_delay_val = self.app.config.get(s, "max_delay", fallback=self.app.config.get(tts_old, "max_delay", fallback="2.0"))
        self.app.entry_max_delay.insert(0, max_delay_val)
        self.app.entry_max_delay.pack(side="left", padx=5)
        
        # Real-time listeners for Entry widgets
        for e in [self.app.entry_delay_char, self.app.entry_max_delay]:
            e.bind("<FocusOut>", lambda event: self.app.logic.apply_realtime_config())
            e.bind("<Return>", lambda event: self.app.logic.apply_realtime_config())
            ContextMenu.add_context_menu(e)

        # Profanity List / Custom Filter
        ctk.CTkLabel(v_f, text="Custom Message Filter (Comma separated):", font=self.app.default_font).pack(padx=15, pady=(10, 0), anchor="w")
        self.app.textbox_filter = ctk.CTkTextbox(v_f, height=80, fg_color="#1E1E1E", font=self.app.default_font)
        self.app.textbox_filter.pack(fill="x", padx=15, pady=10)
        ContextMenu.add_context_menu(self.app.textbox_filter)
        
        # Load existing filter list
        prof_file = os.path.join(get_app_dir(), "resources", "bad_words.txt") if not getattr(sys, 'frozen', False) else os.path.join(get_app_dir(), "bad_words.txt")
        if os.path.exists(prof_file):
            try:
                with open(prof_file, "r", encoding="utf-8") as f:
                    self.app.textbox_filter.insert("1.0", f.read())
            except: pass

        # Save Button for Chat-TTS
        ctk.CTkButton(self.scroll, text="SAVE ALL SETTINGS", height=45, fg_color="#28a745", font=self.app.bold_font,
                       command=self.app.save_chat_settings).pack(fill="x", pady=20)
