import customtkinter as ctk

from .context_menu import ContextMenu
from .ui_theme import COLORS, PAGE_PAD, card, page_header, section_heading


class OptimizerFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        page_header(
            self,
            self.app,
            "Optimizer",
            "Choose CPU behavior and manage programs optimized during streaming.",
        )

        strategy_card = card(self)
        strategy_card.pack(fill="x", padx=PAGE_PAD, pady=(0, 8))
        strategy_inner = ctk.CTkFrame(strategy_card, fg_color="transparent")
        strategy_inner.pack(fill="x", padx=16, pady=12)
        strategy_text = ctk.CTkFrame(strategy_inner, fg_color="transparent")
        strategy_text.pack(side="left", fill="x", expand=True)
        section_heading(
            strategy_text,
            self.app,
            "CPU Strategy",
            "Changes are applied immediately to the Optimizer core pool.",
        )
        switches = ctk.CTkFrame(strategy_inner, fg_color="transparent")
        switches.pack(side="right", padx=(12, 0))
        if not hasattr(self.app, "opt_exclude_c0"):
            self.app.opt_exclude_c0 = ctk.BooleanVar(
                value=self.app.opt_config["Settings"].getboolean(
                    "exclude_core_0", fallback=True
                )
            )
        ctk.CTkSwitch(
            switches,
            text="Exclude Core 0",
            variable=self.app.opt_exclude_c0,
            command=self.app.save_opt_settings,
            font=self.app.default_font,
        ).pack(side="left", padx=8)
        if not hasattr(self.app, "opt_disable_smt"):
            self.app.opt_disable_smt = ctk.BooleanVar(
                value=self.app.opt_config["Settings"].getboolean(
                    "disable_smt", fallback=False
                )
            )
        ctk.CTkSwitch(
            switches,
            text="Disable SMT",
            variable=self.app.opt_disable_smt,
            command=self.app.save_opt_settings,
            font=self.app.default_font,
        ).pack(side="left", padx=8)

        self.opt_tabs = ctk.CTkTabview(
            self,
            corner_radius=14,
            fg_color=COLORS["surface"],
            segmented_button_fg_color=COLORS["surface_alt"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
        )
        self.opt_tabs.pack(
            fill="both", expand=True, padx=PAGE_PAD, pady=(0, 16)
        )
        self._opt_tab_titles = {
            "games": self.app.tr("Programs"),
            "directories": self.app.tr("Directories"),
        }
        self.setup_games_tab(self.opt_tabs.add(self._opt_tab_titles["games"]))
        self.setup_dirs_tab(self.opt_tabs.add(self._opt_tab_titles["directories"]))

    def setup_games_tab(self, tab):
        self.app.opt_priority_var = ctk.StringVar(value="P-CORE")
        add_modes = ctk.CTkTabview(
            tab,
            height=170,
            fg_color=COLORS["surface_alt"],
            segmented_button_fg_color=COLORS["surface"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
        )
        add_modes.pack(fill="x", pady=(4, 10))
        self.add_modes = add_modes
        self._add_mode_titles = {
            "quick": self.app.tr("Quick Add"),
            "manual": self.app.tr("Manual Entry"),
        }

        quick_tab = add_modes.add(self._add_mode_titles["quick"])
        quick_inner = ctk.CTkFrame(quick_tab, fg_color="transparent")
        quick_inner.pack(fill="x", padx=8, pady=8)
        self.app.process_search_var = ctk.StringVar()
        self.app.process_search_entry = ctk.CTkEntry(
            quick_inner,
            textvariable=self.app.process_search_var,
            placeholder_text="Search running processes...",
            height=36,
            font=self.app.default_font,
        )
        self.app.process_search_entry.pack(fill="x", pady=(0, 6))
        quick_row = ctk.CTkFrame(quick_inner, fg_color="transparent")
        quick_row.pack(fill="x")
        self.app.running_process_var = ctk.StringVar(value="No running process found")
        self.app.running_process_menu = ctk.CTkOptionMenu(
            quick_row,
            values=["No running process found"],
            variable=self.app.running_process_var,
            height=36,
            font=self.app.default_font,
        )
        self.app.running_process_menu.pack(side="left", expand=True, fill="x")
        ctk.CTkOptionMenu(
            quick_row,
            values=["P-CORE", "E-CORE", "NORMAL"],
            variable=self.app.opt_priority_var,
            width=112,
            height=36,
            font=self.app.default_font,
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            quick_row,
            text="Add Selected",
            width=110,
            height=36,
            command=self.app.add_selected_process,
            font=self.app.bold_font,
        ).pack(side="left")
        ContextMenu.add_context_menu(self.app.process_search_entry)
        self.app.process_search_var.trace_add(
            "write", lambda *_: self.app.filter_running_processes()
        )

        manual_tab = add_modes.add(self._add_mode_titles["manual"])
        manual_inner = ctk.CTkFrame(manual_tab, fg_color="transparent")
        manual_inner.pack(fill="x", padx=8, pady=10)
        self.app.entry_new_game = ctk.CTkEntry(
            manual_inner,
            placeholder_text="game.exe",
            height=36,
            font=self.app.default_font,
        )
        self.app.entry_new_game.pack(side="left", expand=True, fill="x")
        ContextMenu.add_context_menu(self.app.entry_new_game)
        self.app.opt_prio_menu = ctk.CTkOptionMenu(
            manual_inner,
            values=["P-CORE", "E-CORE", "NORMAL"],
            variable=self.app.opt_priority_var,
            width=112,
            height=36,
            font=self.app.default_font,
        )
        self.app.opt_prio_menu.pack(side="left", padx=6)
        ctk.CTkButton(
            manual_inner,
            text="Browse .exe",
            width=100,
            height=36,
            command=self.app.browse_opt_target,
            font=self.app.default_font,
            fg_color=COLORS["surface_hover"],
            hover_color=COLORS["border"],
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            manual_inner,
            text="Add",
            width=70,
            height=36,
            command=self.app.add_opt_target,
            font=self.app.bold_font,
        ).pack(side="left")

        list_header = ctk.CTkFrame(tab, fg_color="transparent")
        list_header.pack(fill="x", padx=4, pady=(0, 5))
        ctk.CTkLabel(
            list_header, text="Managed Programs", font=self.app.section_font
        ).pack(side="left")
        ctk.CTkLabel(
            list_header,
            text="Process priority and preferred core group",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(side="right")
        self.app.g_scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color=COLORS["surface_alt"],
            corner_radius=10,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["surface_hover"],
        )
        self.app.g_scroll.pack(fill="both", expand=True)

        self.app.refresh_opt_list()
        self.app.after(200, self.app.refresh_running_processes)

    def setup_dirs_tab(self, tab):
        toolbar = ctk.CTkFrame(tab, fg_color=COLORS["surface_alt"], corner_radius=10)
        toolbar.pack(fill="x", pady=(4, 10))
        toolbar_inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        toolbar_inner.pack(fill="x", padx=12, pady=12)
        toolbar_text = ctk.CTkFrame(toolbar_inner, fg_color="transparent")
        toolbar_text.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            toolbar_text, text="Managed Directories", font=self.app.bold_font
        ).pack(anchor="w")
        ctk.CTkLabel(
            toolbar_text,
            text="Apply a preferred core group to programs launched from a folder.",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(2, 0))
        self.app.opt_dir_prio_menu = ctk.CTkOptionMenu(
            toolbar_inner,
            values=["P-CORE", "E-CORE"],
            width=112,
            height=36,
            font=self.app.default_font,
        )
        self.app.opt_dir_prio_menu.pack(side="left", padx=8)
        ctk.CTkButton(
            toolbar_inner,
            text="Add Managed Directory",
            width=180,
            height=36,
            command=self.app.add_opt_path,
            font=self.app.bold_font,
        ).pack(side="left")

        self.app.d_scroll = ctk.CTkScrollableFrame(
            tab,
            fg_color=COLORS["surface_alt"],
            corner_radius=10,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["surface_hover"],
        )
        self.app.d_scroll.pack(fill="both", expand=True)
        self.app.refresh_path_list()

    def apply_language(self):
        for key, english_title in (("games", "Programs"), ("directories", "Directories")):
            current_title = self._opt_tab_titles[key]
            translated_title = self.app.tr(english_title)
            if translated_title != current_title:
                self.opt_tabs.rename(current_title, translated_title)
                self._opt_tab_titles[key] = translated_title

        for key, english_title in (("quick", "Quick Add"), ("manual", "Manual Entry")):
            current_title = self._add_mode_titles[key]
            translated_title = self.app.tr(english_title)
            if translated_title != current_title:
                self.add_modes.rename(current_title, translated_title)
                self._add_mode_titles[key] = translated_title
