import os
import sys

import customtkinter as ctk

from core.app_logger import get_app_dir

from .context_menu import ContextMenu
from .ui_theme import COLORS, PAGE_PAD, card, page_header, section_heading


class ChatFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def _show_voice_provider(self, provider):
        """Show only the settings that belong to the selected voice provider."""
        if provider not in self.provider_frames:
            provider = "edge"
        if self.app.voice_provider.get() != provider:
            self.app.voice_provider.set(provider)
        self.provider_frames[provider].tkraise()

    def _field(self, parent, title, widget, row, column, columnspan=1, warning=False):
        ctk.CTkLabel(
            parent,
            text=title,
            font=self.app.small_font,
            text_color=COLORS["warning"] if warning else COLORS["muted"],
        ).grid(
            row=row * 2,
            column=column,
            columnspan=columnspan,
            sticky="w",
            padx=6,
            pady=(5, 3),
        )
        widget.grid(
            row=row * 2 + 1,
            column=column,
            columnspan=columnspan,
            sticky="ew",
            padx=6,
            pady=(0, 5),
        )
        return widget

    def setup_ui(self):
        page_header(
            self,
            self.app,
            "Bot Live Chat",
            "Connect live chats and choose how messages are spoken.",
        )
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["surface_alt"],
            scrollbar_button_hover_color=COLORS["surface_hover"],
        )
        self.scroll.pack(fill="both", expand=True, padx=PAGE_PAD, pady=(0, 16))

        control_card = card(self.scroll)
        control_card.pack(fill="x", pady=(0, 10))
        control_inner = ctk.CTkFrame(control_card, fg_color="transparent")
        control_inner.pack(fill="x", padx=16, pady=14)
        control_text = ctk.CTkFrame(control_inner, fg_color="transparent")
        control_text.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            control_text, text="Engine Control", font=self.app.section_font
        ).pack(anchor="w")
        ctk.CTkLabel(
            control_text,
            text="Start or stop speech for every enabled platform.",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(2, 0))
        engine_running = bool(self.app.engine.is_running)
        self.app.btn_toggle_tts_chat = ctk.CTkButton(
            control_inner,
            text="STOP BOT LIVE CHAT" if engine_running else "START BOT LIVE CHAT",
            height=42,
            width=210,
            fg_color=COLORS["danger"] if engine_running else COLORS["success"],
            hover_color=(
                COLORS["danger_hover"] if engine_running else COLORS["success_hover"]
            ),
            font=self.app.bold_font,
            command=self.app.toggle_tts,
        )
        self.app.btn_toggle_tts_chat.pack(side="right", padx=(14, 0))

        connections = card(self.scroll)
        connections.pack(fill="x", pady=10)
        connection_inner = ctk.CTkFrame(connections, fg_color="transparent")
        connection_inner.pack(fill="x", padx=16, pady=14)
        section_heading(
            connection_inner,
            self.app,
            "Live Chat Connections",
            "Enable only the platforms you want Bot Live Chat to monitor.",
        )
        platform_grid = ctk.CTkFrame(connection_inner, fg_color="transparent")
        platform_grid.pack(fill="x", pady=(10, 0))
        for column in range(3):
            platform_grid.grid_columnconfigure(column, weight=1, uniform="platforms")

        platforms = (
            ("YouTube Live", self.app.yt_enabled, "entry_yt", "Video ID or URL"),
            ("Twitch Chat", self.app.tw_enabled, "entry_tw", "Channel Name"),
            ("TikTok Live", self.app.tk_enabled, "entry_tk", "@username"),
        )
        settings_section = "settings"
        old_section = "tts"
        for column, (platform, variable, entry_attr, placeholder) in enumerate(platforms):
            platform_card = ctk.CTkFrame(
                platform_grid,
                fg_color=COLORS["surface_alt"],
                corner_radius=10,
            )
            platform_card.grid(row=0, column=column, sticky="nsew", padx=5)
            ctk.CTkLabel(
                platform_card, text=platform, font=self.app.bold_font
            ).pack(anchor="w", padx=12, pady=(10, 5))
            ctk.CTkCheckBox(
                platform_card,
                text="Enabled",
                variable=variable,
                onvalue="True",
                offvalue="False",
                font=self.app.default_font,
            ).pack(anchor="w", padx=12, pady=(0, 8))
            entry = ctk.CTkEntry(
                platform_card,
                height=36,
                placeholder_text=placeholder,
                font=self.app.default_font,
            )
            setattr(self.app, entry_attr, entry)
            if platform == "YouTube Live":
                value = self.app.config.get(
                    settings_section,
                    "yt_video_id",
                    fallback=self.app.config.get(
                        old_section,
                        "youtube_video_id",
                        fallback=self.app.config.get(
                            settings_section, "YOUTUBE_VIDEO_ID", fallback=""
                        ),
                    ),
                )
            elif platform == "Twitch Chat":
                value = self.app.config.get(
                    settings_section,
                    "tw_channel",
                    fallback=self.app.config.get(old_section, "tw_channel", fallback=""),
                )
            else:
                value = self.app.config.get(
                    settings_section,
                    "tk_username",
                    fallback=self.app.config.get(old_section, "tk_username", fallback=""),
                )
            entry.insert(0, value)
            entry.pack(fill="x", padx=12, pady=(0, 12))
            ContextMenu.add_context_menu(entry)

        voice_card = card(self.scroll)
        voice_card.pack(fill="x", pady=10)
        voice_inner = ctk.CTkFrame(voice_card, fg_color="transparent")
        voice_inner.pack(fill="x", padx=16, pady=14)
        voice_header = ctk.CTkFrame(voice_inner, fg_color="transparent")
        voice_header.pack(fill="x")
        voice_text = ctk.CTkFrame(voice_header, fg_color="transparent")
        voice_text.pack(side="left", fill="x", expand=True)
        section_heading(
            voice_text,
            self.app,
            "Voice & Provider",
            "Provider-specific fields appear only when that provider is selected.",
        )
        self.provider_menu = ctk.CTkOptionMenu(
            voice_header,
            values=["edge", "gtts", "gemini", "openai"],
            variable=self.app.voice_provider,
            command=self._show_voice_provider,
            font=self.app.default_font,
            width=150,
            height=36,
        )
        self.provider_menu.pack(side="right", padx=(12, 0))

        provider_container = ctk.CTkFrame(
            voice_inner, fg_color=COLORS["surface_alt"], corner_radius=10
        )
        provider_container.pack(fill="x", pady=(10, 0))
        provider_container.grid_columnconfigure(0, weight=1)
        self.provider_frames = {}

        edge_frame = ctk.CTkFrame(provider_container, fg_color="transparent")
        edge_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=8)
        edge_frame.grid_columnconfigure(0, weight=1)
        self.provider_frames["edge"] = edge_frame
        self.voice_menu = ctk.CTkOptionMenu(
            edge_frame,
            values=["th-TH-PremwadeeNeural", "th-TH-NiwatNeural"],
            variable=self.app.voice_var,
            height=36,
        )
        self._field(edge_frame, "Voice Model:", self.voice_menu, 0, 0)

        gtts_frame = ctk.CTkFrame(provider_container, fg_color="transparent")
        gtts_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=8)
        gtts_frame.grid_columnconfigure(0, weight=1)
        self.provider_frames["gtts"] = gtts_frame
        gtts_menu = ctk.CTkOptionMenu(
            gtts_frame,
            values=["th", "en"],
            variable=self.app.gtts_language,
            height=36,
        )
        self._field(gtts_frame, "gTTS Language:", gtts_menu, 0, 0)

        gemini_frame = ctk.CTkFrame(provider_container, fg_color="transparent")
        gemini_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=8)
        for column in range(2):
            gemini_frame.grid_columnconfigure(column, weight=1, uniform="gemini_fields")
        self.provider_frames["gemini"] = gemini_frame
        gemini_voices = ["Kore", "Puck", "Charon", "Fenrir", "Leda", "Orus", "Aoede", "Zephyr"]
        self._field(
            gemini_frame,
            "Gemini Voice:",
            ctk.CTkOptionMenu(
                gemini_frame, values=gemini_voices,
                variable=self.app.gemini_voice, height=36,
            ),
            0,
            0,
        )
        self._field(
            gemini_frame,
            "Gemini Model:",
            ctk.CTkOptionMenu(
                gemini_frame,
                values=[
                    "gemini-3.1-flash-tts-preview",
                    "gemini-2.5-flash-preview-tts",
                    "gemini-2.5-pro-preview-tts",
                ],
                variable=self.app.gemini_model,
                height=36,
            ),
            0,
            1,
        )
        self.app.entry_gemini_key = ctk.CTkEntry(
            gemini_frame,
            textvariable=self.app.gemini_api_key,
            show="•",
            placeholder_text="GEMINI_API_KEY environment variable",
            height=36,
        )
        self._field(
            gemini_frame,
            "Gemini API Key (Experimental):",
            self.app.entry_gemini_key,
            1,
            0,
            warning=True,
        )
        self.app.entry_gemini_style = ctk.CTkEntry(
            gemini_frame, textvariable=self.app.gemini_style, height=36
        )
        self._field(
            gemini_frame,
            "Voice Style:",
            self.app.entry_gemini_style,
            1,
            1,
        )
        ContextMenu.add_context_menu(self.app.entry_gemini_key)
        ContextMenu.add_context_menu(self.app.entry_gemini_style)

        openai_frame = ctk.CTkFrame(provider_container, fg_color="transparent")
        openai_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=8)
        for column in range(3):
            openai_frame.grid_columnconfigure(column, weight=1, uniform="openai_fields")
        self.provider_frames["openai"] = openai_frame
        self._field(
            openai_frame,
            "OpenAI Model:",
            ctk.CTkOptionMenu(
                openai_frame,
                values=["tts-1", "tts-1-hd", "gpt-4o-mini-tts"],
                variable=self.app.openai_model,
                height=36,
            ),
            0,
            0,
        )
        openai_voices = [
            "alloy", "ash", "ballad", "coral", "echo", "fable", "onyx",
            "nova", "sage", "shimmer", "verse", "marin", "cedar",
        ]
        self._field(
            openai_frame,
            "OpenAI Voice:",
            ctk.CTkOptionMenu(
                openai_frame,
                values=openai_voices,
                variable=self.app.openai_voice,
                height=36,
            ),
            0,
            1,
        )
        self.app.entry_openai_speed = ctk.CTkEntry(
            openai_frame, textvariable=self.app.openai_speed, height=36
        )
        self._field(
            openai_frame,
            "Speed (0.25-4.0):",
            self.app.entry_openai_speed,
            0,
            2,
        )
        self.app.entry_openai_key = ctk.CTkEntry(
            openai_frame,
            textvariable=self.app.openai_api_key,
            show="•",
            placeholder_text="OPENAI_API_KEY environment variable",
            height=36,
        )
        self._field(
            openai_frame,
            "OpenAI API Key (Experimental):",
            self.app.entry_openai_key,
            1,
            0,
            warning=True,
        )
        self.app.entry_openai_style = ctk.CTkEntry(
            openai_frame, textvariable=self.app.openai_instructions, height=36
        )
        self._field(
            openai_frame,
            "OpenAI Voice Style:",
            self.app.entry_openai_style,
            1,
            1,
            columnspan=2,
        )
        for entry in (
            self.app.entry_openai_key,
            self.app.entry_openai_style,
            self.app.entry_openai_speed,
        ):
            ContextMenu.add_context_menu(entry)

        self._show_voice_provider(self.app.voice_provider.get())

        behavior_card = card(self.scroll)
        behavior_card.pack(fill="x", pady=10)
        behavior_inner = ctk.CTkFrame(behavior_card, fg_color="transparent")
        behavior_inner.pack(fill="x", padx=16, pady=14)
        section_heading(
            behavior_inner,
            self.app,
            "Speech Behavior",
            "Control translation, filtering, and speaking delay.",
        )
        option_row = ctk.CTkFrame(behavior_inner, fg_color="transparent")
        option_row.pack(fill="x", pady=(10, 6))
        ctk.CTkCheckBox(
            option_row,
            text="Auto-Translate (TH)",
            variable=self.app.auto_translate,
            onvalue="True",
            offvalue="False",
            font=self.app.default_font,
        ).pack(side="left", padx=(0, 18))
        ctk.CTkCheckBox(
            option_row,
            text="Filter Profanity",
            variable=self.app.profanity_enabled,
            onvalue="True",
            offvalue="False",
            font=self.app.default_font,
        ).pack(side="left")

        delay_row = ctk.CTkFrame(behavior_inner, fg_color="transparent")
        delay_row.pack(fill="x", pady=6)
        ctk.CTkLabel(
            delay_row, text="Delay/Char:", font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(side="left")
        self.app.entry_delay_char = ctk.CTkEntry(delay_row, width=80, height=34)
        delay_value = self.app.config.get(
            settings_section,
            "delay_per_char",
            fallback=self.app.config.get(old_section, "delay_per_char", fallback="0.03"),
        )
        self.app.entry_delay_char.insert(0, delay_value)
        self.app.entry_delay_char.pack(side="left", padx=(6, 18))
        ctk.CTkLabel(
            delay_row, text="Max Delay:", font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(side="left")
        self.app.entry_max_delay = ctk.CTkEntry(delay_row, width=80, height=34)
        max_delay_value = self.app.config.get(
            settings_section,
            "max_delay",
            fallback=self.app.config.get(old_section, "max_delay", fallback="2.0"),
        )
        self.app.entry_max_delay.insert(0, max_delay_value)
        self.app.entry_max_delay.pack(side="left", padx=6)
        for entry in (self.app.entry_delay_char, self.app.entry_max_delay):
            entry.bind("<FocusOut>", lambda _event: self.app.logic.apply_realtime_config())
            entry.bind("<Return>", lambda _event: self.app.logic.apply_realtime_config())
            ContextMenu.add_context_menu(entry)

        ctk.CTkLabel(
            behavior_inner,
            text="Custom Message Filter (Comma separated):",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(8, 4))
        self.app.textbox_filter = ctk.CTkTextbox(
            behavior_inner,
            height=82,
            fg_color=COLORS["input"],
            border_width=1,
            border_color=COLORS["border"],
            font=self.app.default_font,
        )
        self.app.textbox_filter.pack(fill="x")
        ContextMenu.add_context_menu(self.app.textbox_filter)

        profanity_file = (
            os.path.join(get_app_dir(), "resources", "bad_words.txt")
            if not getattr(sys, "frozen", False)
            else os.path.join(get_app_dir(), "bad_words.txt")
        )
        if os.path.exists(profanity_file):
            try:
                with open(profanity_file, "r", encoding="utf-8") as file:
                    self.app.textbox_filter.insert("1.0", file.read())
            except Exception:
                pass

        ctk.CTkButton(
            self.scroll,
            text="SAVE ALL SETTINGS",
            height=44,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            font=self.app.bold_font,
            command=self.app.save_chat_settings,
        ).pack(fill="x", pady=(10, 4))
