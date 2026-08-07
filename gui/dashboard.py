import customtkinter as ctk

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        # KPI Cards
        top_stats = ctk.CTkFrame(self, fg_color="transparent")
        top_stats.pack(fill="x", pady=10)
        
        self.status_card = ctk.CTkFrame(top_stats, corner_radius=15, fg_color="#2D2D2D", height=100)
        self.status_card.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(self.status_card, text="SYSTEM STATUS", font=self.app.default_font).pack(pady=(15, 0))
        self.status_label = ctk.CTkLabel(self.status_card, text="IDLE", font=self.app.title_font, text_color="#ABB2BF")
        self.status_label.pack(pady=(0, 15))

        card_p = ctk.CTkFrame(top_stats, corner_radius=15, fg_color="#2D2D2D")
        card_p.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(card_p, text="P-CORE USAGE", font=self.app.default_font).pack(pady=(10, 0))
        self.pcore_lbl = ctk.CTkLabel(card_p, text="0%", font=self.app.title_font, text_color="#28a745")
        self.pcore_lbl.pack()
        self.pcore_count_lbl = ctk.CTkLabel(
            card_p,
            text=f"{self.app.tr('Optimizer uses')} 0 / 0 {self.app.tr('logical cores')}",
            font=self.app.default_font,
            text_color="#ABB2BF",
        )
        self.pcore_count_lbl.pack(pady=(0, 10))

        card_e = ctk.CTkFrame(top_stats, corner_radius=15, fg_color="#2D2D2D")
        card_e.pack(side="left", expand=True, fill="both", padx=10)
        ctk.CTkLabel(card_e, text="E-CORE USAGE", font=self.app.default_font).pack(pady=(10, 0))
        self.ecore_lbl = ctk.CTkLabel(card_e, text="N/A", font=self.app.title_font, text_color="#17a2b8")
        self.ecore_lbl.pack()
        self.ecore_count_lbl = ctk.CTkLabel(
            card_e,
            text=f"{self.app.tr('Optimizer uses')} 0 / 0 {self.app.tr('logical cores')}",
            font=self.app.default_font,
            text_color="#ABB2BF",
        )
        self.ecore_count_lbl.pack(pady=(0, 10))

        # Main Controls
        ctrl_frame = ctk.CTkFrame(self, fg_color="#2D2D2D", corner_radius=15)
        ctrl_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(ctrl_frame, text="Master Control Panel", font=self.app.bold_font).pack(pady=10)
        
        self.btn_toggle_tts = ctk.CTkButton(ctrl_frame, text="START BOT LIVE CHAT", height=50, fg_color="#28a745",
                                            font=self.app.bold_font, command=self.app.toggle_tts)
        self.btn_toggle_tts.pack(side="left", expand=True, fill="x", padx=20, pady=20)
        
        self.btn_toggle_opt = ctk.CTkButton(ctrl_frame, text="START OPTIMIZER", height=50, fg_color="#17a2b8", 
                                            font=self.app.bold_font, command=self.app.toggle_optimizer)
        self.btn_toggle_opt.pack(side="left", expand=True, fill="x", padx=20, pady=20)

        # Keep each subsystem's console readable without adding more panels.
        self.log_tabs = ctk.CTkTabview(self, corner_radius=15, fg_color="#252525")
        self.log_tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_boxes = {}
        self._log_tab_titles = {}
        from .context_menu import ContextMenu

        for key, title in (
            ("all", "All Logs"),
            ("chat", "Bot Live Chat"),
            ("optimizer", "Optimizer"),
        ):
            translated_title = self.app.tr(title)
            tab = self.log_tabs.add(translated_title)
            log_box = ctk.CTkTextbox(
                tab,
                corner_radius=10,
                fg_color="#1E1E1E",
                border_width=1,
                border_color="#333333",
            )
            log_box.pack(fill="both", expand=True, padx=4, pady=4)
            log_box.configure(state="disabled")
            ContextMenu.add_context_menu(log_box)
            self.log_boxes[key] = log_box
            self._log_tab_titles[key] = translated_title

        # Compatibility alias for code that expects the combined console.
        self.log_box = self.log_boxes["all"]

    def clear_log(self, category="all"):
        log_box = self.log_boxes.get(category)
        if log_box is None:
            return
        log_box.configure(state="normal")
        log_box.delete("1.0", "end")
        log_box.configure(state="disabled")

    def apply_language(self):
        for key, english_title in (
            ("all", "All Logs"),
            ("chat", "Bot Live Chat"),
            ("optimizer", "Optimizer"),
        ):
            current_title = self._log_tab_titles[key]
            translated_title = self.app.tr(english_title)
            if translated_title != current_title:
                self.log_tabs.rename(current_title, translated_title)
                self._log_tab_titles[key] = translated_title
