import customtkinter as ctk

from .context_menu import ContextMenu
from .ui_theme import CARD_RADIUS, COLORS, PAGE_PAD, page_header


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        page_header(
            self,
            self.app,
            "Dashboard",
            "Live system performance and service controls at a glance.",
        )

        # Logs still belong to Dashboard, but no longer compete with the live
        # performance overview for vertical space.
        self.dashboard_tabs = ctk.CTkTabview(
            self,
            corner_radius=CARD_RADIUS,
            fg_color=COLORS["surface"],
            segmented_button_fg_color=COLORS["surface_alt"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
        )
        self.dashboard_tabs.pack(
            fill="both", expand=True, padx=PAGE_PAD, pady=(0, 16)
        )
        self._dashboard_tab_titles = {
            "performance": self.app.tr("Performance"),
            "logs": self.app.tr("Logs"),
        }
        performance_tab = self.dashboard_tabs.add(self._dashboard_tab_titles["performance"])
        logs_tab = self.dashboard_tabs.add(self._dashboard_tab_titles["logs"])

        # Compact resource cards.
        top_stats = ctk.CTkFrame(performance_tab, fg_color="transparent")
        top_stats.pack(fill="x", pady=(6, 8))
        for column in range(4):
            top_stats.grid_columnconfigure(column, weight=1, uniform="dashboard_stats")

        card_p = self._create_stat_card(top_stats, 0, "P-CORE USAGE", "#28a745")
        self.pcore_lbl = card_p[0]
        self.pcore_count_lbl = card_p[1]

        card_e = self._create_stat_card(top_stats, 1, "E-CORE USAGE", "#17a2b8")
        self.ecore_lbl = card_e[0]
        self.ecore_count_lbl = card_e[1]
        self.ecore_lbl.configure(text="N/A")

        card_ram = self._create_stat_card(top_stats, 2, "RAM USAGE", "#f0ad4e")
        self.ram_lbl = card_ram[0]
        self.ram_detail_lbl = card_ram[1]

        card_gpu = self._create_stat_card(top_stats, 3, "GPU USAGE", "#c678dd")
        self.gpu_lbl = card_gpu[0]
        self.gpu_detail_lbl = card_gpu[1]
        self.gpu_lbl.configure(text="N/A")

        # Main controls and the global running state share one compact panel.
        self.status_card = ctk.CTkFrame(
            performance_tab,
            fg_color=COLORS["surface_alt"],
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.status_card.pack(fill="x", pady=8)
        status_header = ctk.CTkFrame(self.status_card, fg_color="transparent")
        status_header.pack(fill="x", padx=18, pady=(10, 0))
        ctk.CTkLabel(
            status_header, text="Master Control Panel", font=self.app.bold_font
        ).pack(side="left")
        ctk.CTkLabel(
            status_header, text="SYSTEM STATUS", font=self.app.default_font,
            text_color=COLORS["muted"],
        ).pack(side="right", padx=(8, 0))
        self.status_label = ctk.CTkLabel(
            status_header, text="IDLE", font=self.app.bold_font, text_color=COLORS["muted"]
        )
        self.status_label.pack(side="right")

        controls = ctk.CTkFrame(self.status_card, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=(6, 12))
        self.btn_toggle_tts = ctk.CTkButton(
            controls,
            text="START BOT LIVE CHAT",
            height=42,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            font=self.app.bold_font,
            command=self.app.toggle_tts,
        )
        self.btn_toggle_tts.pack(side="left", expand=True, fill="x", padx=8)
        self.btn_toggle_opt = ctk.CTkButton(
            controls,
            text="START OPTIMIZER",
            height=42,
            fg_color=COLORS["cyan"],
            font=self.app.bold_font,
            command=self.app.toggle_optimizer,
        )
        self.btn_toggle_opt.pack(side="left", expand=True, fill="x", padx=8)

        # A single batched text widget is substantially cheaper to refresh than
        # rebuilding dozens of labels every sample.
        usage_panel = ctk.CTkFrame(
            performance_tab,
            fg_color=COLORS["surface_alt"],
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=COLORS["border"],
        )
        usage_panel.pack(fill="both", expand=True, pady=(8, 6))
        self.process_usage_title = ctk.CTkLabel(
            usage_panel, text="Top Programs", font=self.app.bold_font
        )
        self.process_usage_title.pack(anchor="w", padx=14, pady=(10, 4))
        self.process_usage_box = ctk.CTkTextbox(
            usage_panel,
            corner_radius=10,
            fg_color=COLORS["input"],
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",
        )
        self.process_usage_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.process_usage_box.insert("1.0", self.app.tr("Collecting performance data...") + "\n")
        self.process_usage_box.configure(state="disabled")
        self._last_process_usage_text = None
        ContextMenu.add_context_menu(self.process_usage_box)

        # Focused log tabs remain available under Dashboard > Logs.
        self.log_tabs = ctk.CTkTabview(
            logs_tab,
            corner_radius=CARD_RADIUS,
            fg_color=COLORS["surface_alt"],
            segmented_button_fg_color=COLORS["surface"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
        )
        self.log_tabs.pack(fill="both", expand=True, padx=2, pady=2)
        self.log_boxes = {}
        self._log_tab_titles = {}
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
                fg_color=COLORS["input"],
                border_width=1,
                border_color=COLORS["border"],
            )
            log_box.pack(fill="both", expand=True, padx=4, pady=4)
            log_box.configure(state="disabled")
            ContextMenu.add_context_menu(log_box)
            self.log_boxes[key] = log_box
            self._log_tab_titles[key] = translated_title

        # Compatibility alias for code that expects the combined console.
        self.log_box = self.log_boxes["all"]

    def _create_stat_card(self, parent, column, title, color):
        card = ctk.CTkFrame(
            parent,
            corner_radius=CARD_RADIUS,
            fg_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=column, sticky="nsew", padx=5)
        ctk.CTkLabel(card, text=title, font=self.app.default_font).pack(pady=(9, 0))
        value_label = ctk.CTkLabel(card, text="0%", font=self.app.title_font, text_color=color)
        value_label.pack()
        detail_label = ctk.CTkLabel(
            card, text="--", font=self.app.small_font, text_color=COLORS["muted"]
        )
        detail_label.pack(pady=(0, 9))
        return value_label, detail_label

    def render_process_usage(self, rows):
        """Replace the whole process table in one Tk update."""
        program = self.app.tr("Program")
        cpu = self.app.tr("CPU")
        ram = self.app.tr("RAM")
        gpu = self.app.tr("GPU")
        lines = [f"{program:<34.34} {cpu:>8.8} {ram:>15.15} {gpu:>8.8}", "-" * 69]
        for row in rows:
            lines.append(
                f"{row['name']:<34.34} {row['cpu']:>7.1f}% "
                f"{row['ram_mb']:>7.0f} MB ({row['ram']:>4.1f}%) {row['gpu']:>7.1f}%"
            )
        if not rows:
            lines.append(self.app.tr("No active program data"))

        content = "\n".join(lines) + "\n"
        if content == self._last_process_usage_text:
            return
        self._last_process_usage_text = content
        self.process_usage_box.configure(state="normal")
        # Tk's replace command updates the text atomically, avoiding the white
        # blink caused by a visible delete-then-insert refresh.
        self.process_usage_box._textbox.replace("1.0", "end", content)
        self.process_usage_box.configure(state="disabled")

    def clear_log(self, category="all"):
        log_box = self.log_boxes.get(category)
        if log_box is None:
            return
        log_box.configure(state="normal")
        log_box.delete("1.0", "end")
        log_box.configure(state="disabled")

    def apply_language(self):
        for key, english_title in (("performance", "Performance"), ("logs", "Logs")):
            current_title = self._dashboard_tab_titles[key]
            translated_title = self.app.tr(english_title)
            if translated_title != current_title:
                self.dashboard_tabs.rename(current_title, translated_title)
                self._dashboard_tab_titles[key] = translated_title

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
