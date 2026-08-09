import customtkinter as ctk

from .i18n import LANGUAGE_NAMES
from .ui_theme import COLORS, PAGE_PAD, card, page_header, section_heading


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def _switch_row(self, parent, title, description, variable, last=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(8, 4 if last else 8))
        text = ctk.CTkFrame(row, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text, text=title, font=self.app.default_font).pack(anchor="w")
        ctk.CTkLabel(
            text,
            text=description,
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(1, 0))
        ctk.CTkSwitch(row, text="", variable=variable, width=42).pack(
            side="right", padx=(12, 0)
        )
        if not last:
            ctk.CTkFrame(parent, height=1, fg_color=COLORS["border"]).pack(fill="x")

    def setup_ui(self):
        page_header(
            self,
            self.app,
            "App Settings",
            "Personalize language, startup behavior, and Windows integration.",
        )
        container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["surface_alt"],
            scrollbar_button_hover_color=COLORS["surface_hover"],
        )
        container.pack(fill="both", expand=True, padx=PAGE_PAD, pady=(0, 16))

        appearance_card = card(container)
        appearance_card.pack(fill="x", pady=(0, 10))
        appearance_inner = ctk.CTkFrame(appearance_card, fg_color="transparent")
        appearance_inner.pack(fill="x", padx=16, pady=14)
        section_heading(
            appearance_inner,
            self.app,
            "Language & Interface",
            "Language changes are applied immediately without restarting.",
        )
        language_row = ctk.CTkFrame(appearance_inner, fg_color="transparent")
        language_row.pack(fill="x", pady=(12, 0))
        ctk.CTkLabel(
            language_row, text="Language:", font=self.app.default_font
        ).pack(side="left")
        self.language_menu = ctk.CTkOptionMenu(
            language_row,
            values=[LANGUAGE_NAMES["th"], LANGUAGE_NAMES["en-US"]],
            command=self.app.set_language,
            height=36,
            width=170,
            font=self.app.default_font,
        )
        self.language_menu.set(LANGUAGE_NAMES[self.app.language_code])
        self.language_menu.pack(side="right")

        behavior_card = card(container)
        behavior_card.pack(fill="x", pady=10)
        behavior_inner = ctk.CTkFrame(behavior_card, fg_color="transparent")
        behavior_inner.pack(fill="x", padx=16, pady=14)
        section_heading(
            behavior_inner,
            self.app,
            "Startup & Background",
            "Choose how Streamer Suite behaves when Windows or the app starts.",
        )
        self._switch_row(
            behavior_inner,
            "Start Minimized to System Tray",
            "Open quietly in the tray instead of showing the main window.",
            self.app.start_minimized,
        )
        self._switch_row(
            behavior_inner,
            "Run on Windows Startup via Task Scheduler",
            "Launch automatically after you sign in to Windows.",
            self.app.run_on_startup,
        )
        self._switch_row(
            behavior_inner,
            "Auto Start Optimizer after app launch",
            "Start optimization automatically when Streamer Suite is ready.",
            self.app.auto_start_optimizer,
        )
        self._switch_row(
            behavior_inner,
            "Windows Notifications",
            "Show tray notifications for important service events.",
            self.app.windows_notifications,
            last=True,
        )

        info_card = ctk.CTkFrame(
            container,
            fg_color="#172338",
            corner_radius=12,
            border_width=1,
            border_color="#24466E",
        )
        info_card.pack(fill="x", pady=10)
        ctk.CTkLabel(
            info_card,
            text="Task Scheduler runs Streamer Suite with administrator privileges. "
                 "Windows may require confirmation when this setting is changed.",
            font=self.app.small_font,
            text_color="#9CC8FF",
            justify="left",
            wraplength=720,
        ).pack(anchor="w", padx=14, pady=12)

        ctk.CTkButton(
            container,
            text="SAVE SETTINGS",
            height=44,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            font=self.app.bold_font,
            command=self.app.save_app_settings,
        ).pack(fill="x", pady=(10, 4))
