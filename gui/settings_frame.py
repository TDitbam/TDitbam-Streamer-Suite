import customtkinter as ctk
from .i18n import LANGUAGE_NAMES

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)


        # Settings Card
        settings_card = ctk.CTkFrame(container, fg_color="#2D2D2D", corner_radius=15)
        settings_card.pack(fill="both", expand=True, pady=10)

        inner_f = ctk.CTkFrame(settings_card, fg_color="transparent")
        inner_f.pack(fill="both", expand=True, padx=20, pady=20)

        # UI Language
        row_language = ctk.CTkFrame(inner_f, fg_color="transparent")
        row_language.pack(fill="x", pady=10)
        ctk.CTkLabel(row_language, text="Language:", font=self.app.default_font).pack(side="left")
        self.language_menu = ctk.CTkOptionMenu(
            row_language,
            values=[LANGUAGE_NAMES["th"], LANGUAGE_NAMES["en-US"]],
            command=self.app.set_language,
            font=self.app.default_font,
        )
        self.language_menu.set(LANGUAGE_NAMES[self.app.language_code])
        self.language_menu.pack(side="left", padx=10)

        # Start Minimized Option
        row_minimized = ctk.CTkFrame(inner_f, fg_color="transparent")
        row_minimized.pack(fill="x", pady=10)
        ctk.CTkSwitch(
            row_minimized, 
            text="Start Minimized to System Tray",
            variable=self.app.start_minimized, 
            font=self.app.default_font
        ).pack(side="left")

        # Startup Task Scheduler Option
        row_startup = ctk.CTkFrame(inner_f, fg_color="transparent")
        row_startup.pack(fill="x", pady=10)
        ctk.CTkSwitch(
            row_startup, 
            text="Run on Windows Startup via Task Scheduler",
            variable=self.app.run_on_startup, 
            font=self.app.default_font
        ).pack(side="left")

        # Info Box explaining Task Scheduler / UAC bypass
        info_f = ctk.CTkFrame(inner_f, fg_color="#333333", corner_radius=8)
        info_f.pack(fill="x", pady=(20, 0))
        
        desc = (
            "Information:\n"
            "• Start minimized: The app opens directly in the Windows System Tray.\n"
            "• Run on startup: Windows Task Scheduler starts the app when you sign in.\n"
            "• Task Scheduler allows the app to start with administrator privileges without showing a UAC prompt each time."
        )
        ctk.CTkLabel(info_f, text=desc, font=self.app.default_font, text_color="#ABB2BF", justify="left", padx=15, pady=15).pack(anchor="w")

        # Save Button
        ctk.CTkButton(
            inner_f, 
            text="SAVE SETTINGS",
            height=45, 
            fg_color="#28a745", 
            hover_color="#218838", 
            font=self.app.bold_font,
            command=self.app.save_app_settings
        ).pack(fill="x", pady=25)
