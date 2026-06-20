import customtkinter as ctk

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, on_show_frame):
        super().__init__(master, width=200, corner_radius=0, fg_color="#1E1E1E")
        self.app = master
        self.on_show_frame = on_show_frame
        
        ctk.CTkLabel(self, text="STREAMER SUITE", font=self.app.title_font).pack(pady=40)
        
        btn_style = {"height": 45, "corner_radius": 8, "fg_color": "transparent", "hover_color": "#333333", "anchor": "w", "font": self.app.default_font}
        
        self.btn_dash = ctk.CTkButton(self, text="🏠 Dashboard", **btn_style, command=lambda: self.on_show_frame("dashboard"))
        self.btn_dash.pack(pady=5, padx=10, fill="x")
        
        self.btn_chat = ctk.CTkButton(self, text="💬 Chat-TTS", **btn_style, command=lambda: self.on_show_frame("chat"))
        self.btn_chat.pack(pady=5, padx=10, fill="x")
        
        self.btn_opt = ctk.CTkButton(self, text="🚀 Optimizer", **btn_style, command=lambda: self.on_show_frame("optimizer"))
        self.btn_opt.pack(pady=5, padx=10, fill="x")
        
        self.btn_clean = ctk.CTkButton(self, text="🧹 Cleanup", **btn_style, command=lambda: self.on_show_frame("cleanup"))
        self.btn_clean.pack(pady=5, padx=10, fill="x")

        self.btn_win = ctk.CTkButton(self, text="🧰 Windows Tools", **btn_style, command=lambda: self.on_show_frame("windowstools"))
        self.btn_win.pack(pady=5, padx=10, fill="x")

        def show_donation():
            try:
                self.app.clipboard_clear()
                self.app.clipboard_append("0646923502")
                self.app.update()
            except:
                pass
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Donate to Developer", "🧧 ขอบคุณที่สนับสนุนผู้พัฒนาซอฟต์แวร์ครับ!\n\nเบอร์ TrueMoney Wallet:\n👉 0646923502 👈\n\n(ระบบได้คัดลอกเบอร์โทรลงคลิปบอร์ดให้เรียบร้อยแล้ว)")

        donate_style = btn_style.copy()
        donate_style["fg_color"] = "#E65100"
        donate_style["hover_color"] = "#F57C00"
        self.btn_settings = ctk.CTkButton(self, text="⚙️ App Settings", **btn_style, command=lambda: self.on_show_frame("settings"))
        self.btn_settings.pack(side="bottom", pady=(5, 20), padx=10, fill="x")
        self.btn_donate = ctk.CTkButton(self, text="🧧 โดเนท TrueMoney", **donate_style, command=show_donation)
        self.btn_donate.pack(side="bottom", pady=5, padx=10, fill="x")
