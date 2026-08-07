import tkinter.messagebox as messagebox

import customtkinter as ctk

from .ui_theme import COLORS


class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, on_show_frame):
        super().__init__(
            master,
            width=218,
            corner_radius=0,
            fg_color=COLORS["sidebar"],
            border_width=0,
        )
        self.grid_propagate(False)
        self.app = master
        self.on_show_frame = on_show_frame
        self._active_page = None

        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", padx=16, pady=(22, 24))
        mark = ctk.CTkLabel(
            brand,
            text="SS",
            width=42,
            height=42,
            corner_radius=12,
            fg_color=COLORS["accent"],
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
        )
        mark.pack(side="left")
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            brand_text,
            text="STREAMER SUITE",
            font=self.app.bold_font,
            text_color=COLORS["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand_text,
            text="VERSION 3.6.1",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            self,
            text="WORKSPACE",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["muted"],
        ).pack(anchor="w", padx=20, pady=(0, 6))

        self._nav_buttons = {}
        for page, title in (
            ("dashboard", "Dashboard"),
            ("chat", "Bot Live Chat"),
            ("optimizer", "Optimizer"),
            ("cleanup", "Cleanup"),
            ("windowstools", "Windows Tools"),
        ):
            self._add_nav_button(page, title)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=12, pady=(0, 14))
        self.btn_donate = ctk.CTkButton(
            bottom,
            text="Donate TrueMoney",
            height=38,
            fg_color="transparent",
            border_width=1,
            border_color="#8A4B20",
            hover_color="#35261E",
            text_color="#F0A45D",
            anchor="w",
            font=self.app.default_font,
            command=self._show_donation,
        )
        self.btn_donate.pack(fill="x", pady=(0, 6))
        self.btn_settings = ctk.CTkButton(
            bottom,
            text="App Settings",
            height=42,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORS["surface_hover"],
            anchor="w",
            font=self.app.default_font,
            command=lambda: self.on_show_frame("settings"),
        )
        self.btn_settings.pack(fill="x")
        self._nav_buttons["settings"] = self.btn_settings

        # Compatibility aliases used by older code and release builds.
        self.btn_dash = self._nav_buttons["dashboard"]
        self.btn_chat = self._nav_buttons["chat"]
        self.btn_opt = self._nav_buttons["optimizer"]
        self.btn_clean = self._nav_buttons["cleanup"]
        self.btn_win = self._nav_buttons["windowstools"]

    def _add_nav_button(self, page, title):
        button = ctk.CTkButton(
            self,
            text=title,
            height=42,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORS["surface_hover"],
            anchor="w",
            border_spacing=12,
            font=self.app.default_font,
            command=lambda name=page: self.on_show_frame(name),
        )
        button.pack(fill="x", padx=12, pady=2)
        self._nav_buttons[page] = button

    def set_active(self, page):
        if page == self._active_page:
            return
        for name, button in self._nav_buttons.items():
            if name == page:
                button.configure(fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"])
            else:
                button.configure(fg_color="transparent", hover_color=COLORS["surface_hover"])
        self._active_page = page

    def _show_donation(self):
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append("0646923502")
            self.app.update()
        except Exception:
            pass
        messagebox.showinfo(
            "Donate to Developer",
            "ขอบคุณที่สนับสนุนผู้พัฒนาซอฟต์แวร์ครับ!\n\n"
            "TrueMoney Wallet: 0646923502\n\n"
            "คัดลอกหมายเลขลงคลิปบอร์ดแล้ว",
        )
