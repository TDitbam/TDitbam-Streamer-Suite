import customtkinter as ctk
import os
import sys
from tkinter import filedialog

# Fix for ModuleNotFoundError: Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from optimizer.optimizer_core.config_loader import get_targets as get_opt_targets, get_paths as get_opt_paths

class OptimizerFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Settings
        s_f = ctk.CTkFrame(self, fg_color="#2D2D2D", corner_radius=15)
        s_f.pack(fill="x", pady=10, padx=20)
        
        self.app.opt_exclude_c0 = ctk.BooleanVar(value=self.app.opt_config["Settings"].getboolean("exclude_core_0", fallback=True))
        ctk.CTkSwitch(s_f, text="Exclude Core 0", variable=self.app.opt_exclude_c0, command=self.app.save_opt_settings, font=self.app.default_font).pack(pady=5, padx=20, anchor="w")
        self.app.opt_disable_smt = ctk.BooleanVar(value=self.app.opt_config["Settings"].getboolean("disable_smt", fallback=False))
        ctk.CTkSwitch(s_f, text="Disable SMT", variable=self.app.opt_disable_smt, command=self.app.save_opt_settings, font=self.app.default_font).pack(pady=5, padx=20, anchor="w")

        # Tabs
        self.opt_tabs = ctk.CTkTabview(self, corner_radius=15)
        self.opt_tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.setup_games_tab(self.opt_tabs.add("Games"))
        self.setup_dirs_tab(self.opt_tabs.add("Directories"))

    def setup_games_tab(self, tab):
        self.app.g_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.app.g_scroll.pack(fill="both", expand=True)
        ui = ctk.CTkFrame(tab, fg_color="transparent"); ui.pack(fill="x", pady=5)
        self.app.entry_new_game = ctk.CTkEntry(ui, placeholder_text="game.exe", font=self.app.default_font)
        self.app.entry_new_game.pack(side="left", expand=True, fill="x")
        
        from .context_menu import ContextMenu
        ContextMenu.add_context_menu(self.app.entry_new_game)
        
        self.app.opt_prio_menu = ctk.CTkOptionMenu(ui, values=["P-CORE", "E-CORE", "NORMAL"], width=100, font=self.app.default_font)
        self.app.opt_prio_menu.pack(side="left", padx=5)
        ctk.CTkButton(ui, text="Add", width=60, command=self.app.add_opt_target, font=self.app.default_font).pack(side="right")
        self.app.refresh_opt_list()

    def setup_dirs_tab(self, tab):
        self.app.d_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.app.d_scroll.pack(fill="both", expand=True)
        
        ui = ctk.CTkFrame(tab, fg_color="transparent")
        ui.pack(fill="x", pady=5)
        
        self.app.opt_dir_prio_menu = ctk.CTkOptionMenu(ui, values=["P-CORE", "E-CORE"], width=100, font=self.app.default_font)
        self.app.opt_dir_prio_menu.pack(side="left", padx=5)
        
        ctk.CTkButton(ui, text="Add Managed Directory", command=self.app.add_opt_path, font=self.app.default_font).pack(side="left", expand=True, fill="x")
        
        self.app.refresh_path_list()
