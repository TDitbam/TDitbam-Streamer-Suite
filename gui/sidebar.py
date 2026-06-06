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
