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
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(container, text="🧰 Windows System Tools", font=self.app.title_font).pack(pady=(0, 10), anchor="w")

        # Tabview for different tools
        self.tools_tabs = ctk.CTkTabview(container, corner_radius=15)
        self.tools_tabs.pack(fill="both", expand=True)
        
        self.setup_scheduler_tab(self.tools_tabs.add("Scheduler"))
        self.setup_winget_tab(self.tools_tabs.add("WinGet Manager"))

    def setup_scheduler_tab(self, tab):
        container = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # System / Auto-Shutdown Card
        ctk.CTkLabel(container, text="Auto Shutdown Scheduler", font=self.app.bold_font).pack(pady=(0, 10), anchor="w")
        
        sd_card = ctk.CTkFrame(container, fg_color="#2D2D2D", corner_radius=15)
        sd_card.pack(fill="x", pady=5)
        
        inner_f = ctk.CTkFrame(sd_card, fg_color="transparent")
        inner_f.pack(fill="x", padx=20, pady=20)
        
        row = ctk.CTkFrame(inner_f, fg_color="transparent")
        row.pack(fill="x")
        
        ctk.CTkSwitch(row, text="Enable Daily Auto Shutdown", variable=self.app.opt_auto_shutdown, 
                      command=self.app.save_opt_settings, font=self.app.default_font).pack(side="left")
        
        ctk.CTkLabel(row, text="Time (HH:mm):", font=self.app.default_font).pack(side="left", padx=(30, 10))
        
        self.app.entry_shutdown_time = ctk.CTkEntry(row, textvariable=self.app.opt_shutdown_time, width=100, font=self.app.default_font)
        self.app.entry_shutdown_time.pack(side="left")
        
        from .context_menu import ContextMenu
        ContextMenu.add_context_menu(self.app.entry_shutdown_time)
        
        ctk.CTkButton(row, text="Save & Apply", width=100, command=self.app.save_opt_settings, 
                      fg_color="#28a745", hover_color="#218838", font=self.app.bold_font).pack(side="left", padx=15)

        # Info Box
        info_f = ctk.CTkFrame(inner_f, fg_color="#333333", corner_radius=8)
        info_f.pack(fill="x", pady=(15, 0))
        
        desc = ("ℹ️ Information:\n"
                "• This tool uses Windows Task Scheduler to automate your PC shutdown.\n"
                "• The task is set to run 'Daily' at the specified time.\n"
                "• To cancel, uncheck the switch and click 'Save & Apply'.")
        ctk.CTkLabel(info_f, text=desc, font=self.app.default_font, text_color="#ABB2BF", justify="left", padx=15, pady=10).pack(anchor="w")

    def setup_winget_tab(self, tab):
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Search Area
        search_f = ctk.CTkFrame(container, fg_color="#2D2D2D", corner_radius=10)
        search_f.pack(fill="x", pady=(0, 15))
        
        search_inner = ctk.CTkFrame(search_f, fg_color="transparent")
        search_inner.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(search_inner, text="Search Packages:", font=self.app.bold_font).pack(side="left", padx=(0, 10))
        self.winget_search_entry = ctk.CTkEntry(search_inner, placeholder_text="e.g. vscode, discord, chrome", font=self.app.default_font)
        self.winget_search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(search_inner, text="🔍 Search", width=100, command=self.run_winget_search, font=self.app.bold_font).pack(side="left", padx=5)
        ctk.CTkButton(search_inner, text="🔄 Upgrade All", width=120, fg_color="#17a2b8", command=self.run_winget_upgrade_all, font=self.app.bold_font).pack(side="left", padx=5)

        # Install Area
        install_f = ctk.CTkFrame(container, fg_color="#2D2D2D", corner_radius=10)
        install_f.pack(fill="x", pady=(0, 15))
        
        install_inner = ctk.CTkFrame(install_f, fg_color="transparent")
        install_inner.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(install_inner, text="Install Package ID:", font=self.app.bold_font).pack(side="left", padx=(0, 10))
        self.winget_install_entry = ctk.CTkEntry(install_inner, placeholder_text="e.g. Microsoft.VisualStudioCode", font=self.app.default_font)
        self.winget_install_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(install_inner, text="📥 Install", width=100, fg_color="#28a745", hover_color="#218838", command=self.run_winget_install, font=self.app.bold_font).pack(side="left", padx=5)

        # Results Area
        res_label_f = ctk.CTkFrame(container, fg_color="transparent")
        res_label_f.pack(fill="x")
        ctk.CTkLabel(res_label_f, text="Results / Status:", font=self.app.bold_font).pack(side="left")
        
        self.winget_log = ctk.CTkTextbox(container, fg_color="#1E1E1E", font=("Consolas", 12))
        self.winget_log.pack(fill="both", expand=True, pady=(5, 0))
        
        from .context_menu import ContextMenu
        ContextMenu.add_context_menu(self.winget_log)
        ContextMenu.add_context_menu(self.winget_search_entry)

    def run_winget_search(self):
        query = self.winget_search_entry.get().strip()
        if not query: return
        self._run_winget_cmd(f"winget search \"{query}\"")

    def run_winget_upgrade_all(self):
        self._run_winget_cmd("winget upgrade --all")

    def run_winget_install(self):
        pkg_id = self.winget_install_entry.get().strip()
        if not pkg_id: return
        # --accept-package-agreements and --accept-source-agreements for silent install
        self._run_winget_cmd(f"winget install --id {pkg_id} --silent --accept-package-agreements --accept-source-agreements")

    def _run_winget_cmd(self, cmd_str):
        self.winget_log.configure(state="normal")
        self.winget_log.delete("1.0", "end")
        self.winget_log.insert("end", f"[*] Running: {cmd_str}...\n")
        self.winget_log.configure(state="disabled")
        
        import threading
        import subprocess
        
        def _task():
            CREATE_NO_WINDOW = 0x08000000
            try:
                process = subprocess.Popen(cmd_str, shell=True, 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.STDOUT, 
                                          text=True, 
                                          creationflags=CREATE_NO_WINDOW)
                
                for line in process.stdout:
                    self.app.after(0, lambda l=line: self._append_winget_log(l))
                
                process.wait()
                self.app.after(0, lambda: self._append_winget_log("\n[+] Command finished.\n"))
            except Exception as e:
                self.app.after(0, lambda: self._append_winget_log(f"\n[!] Error: {e}\n"))

        threading.Thread(target=_task, daemon=True).start()

    def _append_winget_log(self, text):
        self.winget_log.configure(state="normal")
        self.winget_log.insert("end", text)
        self.winget_log.see("end")
        self.winget_log.configure(state="disabled")
