import customtkinter as ctk
import os
import sys

# Fix for ModuleNotFoundError: Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

class WindowsToolsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        ctk.CTkLabel(container, text="🧰 Windows System Tools", font=self.app.title_font).pack(pady=(0, 20), anchor="w")

        # System / Auto-Shutdown Card
        sd_card = ctk.CTkFrame(container, fg_color="#2D2D2D", corner_radius=15)
        sd_card.pack(fill="x", pady=10)
        
        inner_f = ctk.CTkFrame(sd_card, fg_color="transparent")
        inner_f.pack(fill="x", padx=25, pady=25)

        ctk.CTkLabel(inner_f, text="Auto Shutdown Scheduler", font=self.app.bold_font).pack(pady=(0, 15), anchor="w")
        
        row = ctk.CTkFrame(inner_f, fg_color="transparent")
        row.pack(fill="x")
        
        ctk.CTkSwitch(row, text="Enable Daily Auto Shutdown", variable=self.app.opt_auto_shutdown, 
                      command=self.app.save_opt_settings, font=self.app.default_font).pack(side="left")
        
        ctk.CTkLabel(row, text="Time (HH:mm):", font=self.app.default_font).pack(side="left", padx=(40, 10))
        
        self.app.entry_shutdown_time = ctk.CTkEntry(row, textvariable=self.app.opt_shutdown_time, width=120, font=self.app.default_font)
        self.app.entry_shutdown_time.pack(side="left")
        
        from .context_menu import ContextMenu
        ContextMenu.add_context_menu(self.app.entry_shutdown_time)
        
        ctk.CTkButton(row, text="Save & Apply", width=120, command=self.app.save_opt_settings, 
                      fg_color="#28a745", hover_color="#218838", font=self.app.bold_font).pack(side="left", padx=20)

        # Info Box
        info_f = ctk.CTkFrame(inner_f, fg_color="#333333", corner_radius=8)
        info_f.pack(fill="x", pady=(20, 0))
        
        desc = ("ℹ️ Information:\n"
                "• This tool uses Windows Task Scheduler to automate your PC shutdown.\n"
                "• The task is set to run 'Daily' at the specified time.\n"
                "• To cancel the schedule, simply uncheck the switch and click 'Save & Apply'.")
        ctk.CTkLabel(info_f, text=desc, font=self.app.default_font, text_color="#ABB2BF", justify="left", padx=15, pady=10).pack(anchor="w")
