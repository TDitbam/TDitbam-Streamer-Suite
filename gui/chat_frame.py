import customtkinter as ctk
import os
import sys
from core.app_logger import get_app_dir

class ChatFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def _show_voice_provider(self, provider):
        """Show only the settings that belong to the selected voice provider."""
        if provider not in self.provider_frames:
            provider = "edge"
        self.app.voice_provider.set(provider)
        self.provider_frames[provider].tkraise()

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
        self.app.btn_toggle_tts_chat = ctk.CTkButton(inner_ctrl, text="START BOT LIVE CHAT", height=45, width=200,
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
        
        # Provider selector. Only the selected provider's fields are visible.
        row1 = ctk.CTkFrame(v_f, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(12, 5))
        ctk.CTkLabel(row1, text="Voice Provider:", font=self.app.default_font).pack(side="left")
        self.provider_menu = ctk.CTkOptionMenu(
            row1, values=["edge", "gtts", "gemini", "openai"], variable=self.app.voice_provider,
            command=self._show_voice_provider, font=self.app.default_font, width=160,
        )
        self.provider_menu.pack(side="left", padx=10)

        provider_container = ctk.CTkFrame(v_f, fg_color="#252525", corner_radius=8)
        provider_container.pack(fill="x", padx=15, pady=5)
        provider_container.grid_columnconfigure(0, weight=1)
        self.provider_frames = {}

        edge_frame = ctk.CTkFrame(provider_container, fg_color="transparent")
        edge_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)
        self.provider_frames["edge"] = edge_frame
        ctk.CTkLabel(edge_frame, text="Voice Model:", font=self.app.default_font).pack(side="left")
        self.voice_menu = ctk.CTkOptionMenu(edge_frame, values=["th-TH-PremwadeeNeural", "th-TH-NiwatNeural"], variable=self.app.voice_var, width=230)
        self.voice_menu.pack(side="left", padx=10)

        gtts_frame = ctk.CTkFrame(provider_container, fg_color="transparent")
        gtts_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=10)
        self.provider_frames["gtts"] = gtts_frame
        ctk.CTkLabel(gtts_frame, text="gTTS Language:", font=self.app.default_font).pack(side="left")
        ctk.CTkOptionMenu(gtts_frame, values=["th", "en"], variable=self.app.gtts_language, width=100).pack(side="left", padx=10)

        gemini_frame = ctk.CTkFrame(provider_container, fg_color="transparent")
        gemini_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=8)
        self.provider_frames["gemini"] = gemini_frame
        gemini_top = ctk.CTkFrame(gemini_frame, fg_color="transparent")
        gemini_top.pack(fill="x", pady=2)
        ctk.CTkLabel(gemini_top, text="Gemini Voice:", font=self.app.default_font).pack(side="left")
        gemini_voices = ["Kore", "Puck", "Charon", "Fenrir", "Leda", "Orus", "Aoede", "Zephyr"]
        ctk.CTkOptionMenu(gemini_top, values=gemini_voices, variable=self.app.gemini_voice, width=110).pack(side="left", padx=10)
        ctk.CTkLabel(gemini_top, text="Gemini Model:", font=self.app.default_font).pack(side="left", padx=(15, 0))
        ctk.CTkOptionMenu(
            gemini_top,
            values=["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"],
            variable=self.app.gemini_model, width=230,
        ).pack(side="left", padx=10)
        gemini_bottom = ctk.CTkFrame(gemini_frame, fg_color="transparent")
        gemini_bottom.pack(fill="x", pady=2)
        ctk.CTkLabel(gemini_bottom, text="Gemini API Key (Experimental):", font=self.app.default_font, text_color="#F0AD4E").pack(side="left")
        self.app.entry_gemini_key = ctk.CTkEntry(
            gemini_bottom, textvariable=self.app.gemini_api_key, show="•", width=240,
            placeholder_text="GEMINI_API_KEY environment variable",
        )
        self.app.entry_gemini_key.pack(side="left", padx=10)
        ctk.CTkLabel(gemini_bottom, text="Voice Style:", font=self.app.default_font).pack(side="left", padx=(15, 0))
        self.app.entry_gemini_style = ctk.CTkEntry(gemini_bottom, textvariable=self.app.gemini_style)
        self.app.entry_gemini_style.pack(side="left", fill="x", expand=True, padx=10)
        from .context_menu import ContextMenu
        ContextMenu.add_context_menu(self.app.entry_gemini_key)
        ContextMenu.add_context_menu(self.app.entry_gemini_style)

        openai_frame = ctk.CTkFrame(provider_container, fg_color="transparent")
        openai_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=8)
        self.provider_frames["openai"] = openai_frame
        openai_top = ctk.CTkFrame(openai_frame, fg_color="transparent")
        openai_top.pack(fill="x", pady=2)
        ctk.CTkLabel(openai_top, text="OpenAI Model:", font=self.app.default_font).pack(side="left")
        ctk.CTkOptionMenu(openai_top, values=["tts-1", "tts-1-hd", "gpt-4o-mini-tts"], variable=self.app.openai_model, width=170).pack(side="left", padx=10)
        ctk.CTkLabel(openai_top, text="OpenAI Voice:", font=self.app.default_font).pack(side="left", padx=(15, 0))
        openai_voices = ["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse", "marin", "cedar"]
        ctk.CTkOptionMenu(openai_top, values=openai_voices, variable=self.app.openai_voice, width=110).pack(side="left", padx=10)
        ctk.CTkLabel(openai_top, text="Speed (0.25-4.0):", font=self.app.default_font).pack(side="left", padx=(15, 0))
        self.app.entry_openai_speed = ctk.CTkEntry(openai_top, textvariable=self.app.openai_speed, width=70)
        self.app.entry_openai_speed.pack(side="left", padx=10)

        openai_bottom = ctk.CTkFrame(openai_frame, fg_color="transparent")
        openai_bottom.pack(fill="x", pady=2)
        ctk.CTkLabel(openai_bottom, text="OpenAI API Key (Experimental):", font=self.app.default_font, text_color="#F0AD4E").pack(side="left")
        self.app.entry_openai_key = ctk.CTkEntry(
            openai_bottom, textvariable=self.app.openai_api_key, show="•", width=230,
            placeholder_text="OPENAI_API_KEY environment variable",
        )
        self.app.entry_openai_key.pack(side="left", padx=10)
        ctk.CTkLabel(openai_bottom, text="OpenAI Voice Style:", font=self.app.default_font).pack(side="left", padx=(15, 0))
        self.app.entry_openai_style = ctk.CTkEntry(openai_bottom, textvariable=self.app.openai_instructions)
        self.app.entry_openai_style.pack(side="left", fill="x", expand=True, padx=10)
        for entry in (self.app.entry_openai_key, self.app.entry_openai_style, self.app.entry_openai_speed):
            ContextMenu.add_context_menu(entry)

        self._show_voice_provider(self.app.voice_provider.get())

        # Translation and filtering
        row_options = ctk.CTkFrame(v_f, fg_color="transparent")
        row_options.pack(fill="x", padx=15, pady=5)
        ctk.CTkCheckBox(row_options, text="Auto-Translate (TH)", variable=self.app.auto_translate, onvalue="True", offvalue="False", font=self.app.default_font).pack(side="left", padx=10)
        ctk.CTkCheckBox(row_options, text="Filter Profanity", variable=self.app.profanity_enabled, onvalue="True", offvalue="False", font=self.app.default_font).pack(side="left", padx=10)

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

        # Save Button for Bot Live Chat
        ctk.CTkButton(self.scroll, text="SAVE ALL SETTINGS", height=45, fg_color="#28a745", font=self.app.bold_font,
                       command=self.app.save_chat_settings).pack(fill="x", pady=20)
