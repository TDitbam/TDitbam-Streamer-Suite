import customtkinter as ctk

class CleanupFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        main_c = ctk.CTkFrame(self, fg_color="#2D2D2D", corner_radius=20)
        main_c.pack(pady=30, padx=30, fill="both", expand=True)

        # Maintenance Section
        m_frame = ctk.CTkFrame(main_c, fg_color="transparent")
        m_frame.pack(fill="x", pady=10, padx=20)
        
        self.app.opt_auto_clean = ctk.BooleanVar(value=self.app.opt_config["Settings"].getboolean("auto_cleanup", fallback=False))
        ctk.CTkSwitch(m_frame, text="Auto Junk Cleanup", variable=self.app.opt_auto_clean, command=self.app.save_opt_settings, font=self.app.default_font).pack(side="left", padx=10)
        
        timer_frame = ctk.CTkFrame(m_frame, fg_color="transparent")
        timer_frame.pack(side="right", padx=10)
        ctk.CTkLabel(timer_frame, text="Interval (min):", font=self.app.default_font).pack(side="left")
        self.app.opt_clean_interval = ctk.StringVar(value=self.app.opt_config["Settings"].get("cleanup_interval", "1440"))
        self.app.entry_clean_int = ctk.CTkEntry(timer_frame, textvariable=self.app.opt_clean_interval, width=60, font=self.app.default_font)
        self.app.entry_clean_int.pack(side="left", padx=5)
        ctk.CTkButton(timer_frame, text="Apply", width=60, command=self.app.save_opt_settings, font=self.app.default_font).pack(side="left")

        ctk.CTkButton(main_c, text="SCAN & CLEAN JUNK", height=60, fg_color="#dc3545", font=self.app.bold_font, command=self.app.run_junk_cleanup).pack(pady=20)
        self.app.clean_log = ctk.CTkTextbox(main_c, fg_color="#1E1E1E", corner_radius=10, font=self.app.default_font)
        self.app.clean_log.pack(fill="both", expand=True, padx=20, pady=20)
