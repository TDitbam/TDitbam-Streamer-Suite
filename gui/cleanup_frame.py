import customtkinter as ctk

from .context_menu import ContextMenu
from .ui_theme import COLORS, PAGE_PAD, card, page_header, section_heading


class CleanupFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        page_header(
            self,
            self.app,
            "Cleanup",
            "Remove temporary files manually or on a recurring schedule.",
        )

        controls_card = card(self)
        controls_card.pack(fill="x", padx=PAGE_PAD, pady=(0, 10))
        controls = ctk.CTkFrame(controls_card, fg_color="transparent")
        controls.pack(fill="x", padx=16, pady=14)
        controls_text = ctk.CTkFrame(controls, fg_color="transparent")
        controls_text.pack(fill="x")
        section_heading(
            controls_text,
            self.app,
            "Cleanup Schedule",
            "Automatic cleanup uses the interval below while Optimizer is running.",
        )

        if not hasattr(self.app, "opt_auto_clean"):
            self.app.opt_auto_clean = ctk.BooleanVar(
                value=self.app.opt_config["Settings"].getboolean(
                    "auto_cleanup", fallback=False
                )
            )
        if not hasattr(self.app, "opt_clean_interval"):
            self.app.opt_clean_interval = ctk.StringVar(
                value=self.app.opt_config["Settings"].get("cleanup_interval", "1440")
            )
        settings = ctk.CTkFrame(controls, fg_color="transparent")
        settings.pack(fill="x", pady=(12, 0))
        ctk.CTkSwitch(
            settings,
            text="Auto Junk Cleanup",
            variable=self.app.opt_auto_clean,
            command=self.app.save_opt_settings,
            font=self.app.default_font,
        ).pack(side="left")
        ctk.CTkLabel(
            settings,
            text="Interval (min):",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(side="left", padx=(18, 0))
        self.app.entry_clean_int = ctk.CTkEntry(
            settings,
            textvariable=self.app.opt_clean_interval,
            width=78,
            height=36,
            font=self.app.default_font,
        )
        self.app.entry_clean_int.pack(side="left", padx=6)
        ctk.CTkButton(
            settings,
            text="Apply",
            width=74,
            height=36,
            command=self.app.save_opt_settings,
            font=self.app.bold_font,
        ).pack(side="left")

        action_row = ctk.CTkFrame(self, fg_color="transparent")
        action_row.pack(fill="x", padx=PAGE_PAD, pady=(0, 10))
        ctk.CTkButton(
            action_row,
            text="SCAN & CLEAN JUNK",
            width=230,
            height=42,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            font=self.app.bold_font,
            command=self.app.run_junk_cleanup,
        ).pack(side="right")
        ctk.CTkLabel(
            action_row,
            text="Review cleanup progress and recovered space below.",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(side="left")

        output_card = card(self)
        output_card.pack(
            fill="both", expand=True, padx=PAGE_PAD, pady=(0, 16)
        )
        output_header = ctk.CTkFrame(output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(
            output_header, text="Cleanup Results", font=self.app.section_font
        ).pack(side="left")
        ctk.CTkButton(
            output_header,
            text="Clear",
            width=70,
            height=28,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            hover_color=COLORS["surface_hover"],
            command=self.clear_output,
            font=self.app.small_font,
        ).pack(side="right")
        self.app.clean_log = ctk.CTkTextbox(
            output_card,
            fg_color=COLORS["input"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.app.clean_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.app.clean_log.configure(state="disabled")

        ContextMenu.add_context_menu(self.app.entry_clean_int)
        ContextMenu.add_context_menu(self.app.clean_log)

    def clear_output(self):
        self.app.clean_log.configure(state="normal")
        self.app.clean_log.delete("1.0", "end")
        self.app.clean_log.configure(state="disabled")
