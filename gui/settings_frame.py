import customtkinter as ctk

from core.version import APP_VERSION

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

        updates_card = card(container)
        updates_card.pack(fill="x", pady=10)
        updates_inner = ctk.CTkFrame(updates_card, fg_color="transparent")
        updates_inner.pack(fill="x", padx=16, pady=14)
        section_heading(
            updates_inner,
            self.app,
            "Version & Updates",
            "Check stable GitHub tags without interrupting your work.",
        )

        version_row = ctk.CTkFrame(updates_inner, fg_color="transparent")
        version_row.pack(fill="x", pady=(12, 8))
        self.current_version_title = ctk.CTkLabel(
            version_row, text="Current version", font=self.app.default_font
        )
        self.current_version_title.pack(side="left")
        self.current_version_value = ctk.CTkLabel(
            version_row, text=f"v{APP_VERSION}", font=self.app.bold_font
        )
        self.current_version_value.pack(side="right")

        latest_row = ctk.CTkFrame(updates_inner, fg_color="transparent")
        latest_row.pack(fill="x", pady=8)
        self.latest_tag_title = ctk.CTkLabel(
            latest_row, text="Latest GitHub tag", font=self.app.default_font
        )
        self.latest_tag_title.pack(side="left")
        self.latest_tag_value = ctk.CTkLabel(
            latest_row, text="—", font=self.app.bold_font
        )
        self.latest_tag_value.pack(side="right")

        self.update_status_label = ctk.CTkLabel(
            updates_inner,
            text="",
            anchor="w",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        )
        self.update_status_label.pack(fill="x", pady=(6, 4))

        self._switch_row(
            updates_inner,
            "Automatically check for updates",
            "Check GitHub tags once in the background after the app starts.",
            self.app.auto_check_updates,
            last=True,
        )

        update_buttons = ctk.CTkFrame(updates_inner, fg_color="transparent")
        update_buttons.pack(fill="x", pady=(10, 0))
        self.check_updates_button = ctk.CTkButton(
            update_buttons,
            text="CHECK NOW",
            height=36,
            command=self.app.check_for_updates,
            font=self.app.bold_font,
        )
        self.check_updates_button.pack(side="left", fill="x", expand=True)
        self.open_release_button = ctk.CTkButton(
            update_buttons,
            text="OPEN RELEASE",
            height=36,
            command=self.app.open_update_page,
            font=self.app.bold_font,
            fg_color=COLORS["surface_hover"],
            hover_color=COLORS["border"],
        )
        self.open_release_button.pack(side="left", fill="x", expand=True, padx=(8, 0))

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
        self.refresh_update_state()

    def refresh_update_state(self):
        status_key = self.app.update_status_key
        status_colors = {
            "A new version is available": COLORS["success"],
            "Unable to check for updates": COLORS["danger"],
        }
        self.current_version_title.configure(text=self.app.tr("Current version"))
        self.latest_tag_title.configure(text=self.app.tr("Latest GitHub tag"))
        self.latest_tag_value.configure(
            text=self.app.latest_update_tag or self.app.tr("Not checked")
        )
        self.update_status_label.configure(
            text=self.app.tr(status_key),
            text_color=status_colors.get(status_key, COLORS["muted"]),
        )
        checking = status_key == "Checking GitHub tags..."
        self.check_updates_button.configure(
            text=self.app.tr("CHECKING...") if checking else self.app.tr("CHECK NOW"),
            state="disabled" if checking else "normal",
        )
        self.open_release_button.configure(
            text=self.app.tr("OPEN RELEASE"),
            state="normal" if self.app.latest_update_tag else "disabled",
        )

    def apply_language(self):
        self.language_menu.set(LANGUAGE_NAMES[self.app.language_code])
        self.refresh_update_state()
