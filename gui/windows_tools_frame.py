import customtkinter as ctk
import os
import shutil
import subprocess
import sys
import threading

from .context_menu import ContextMenu
from .ui_theme import COLORS, PAGE_PAD, card, page_header, section_heading

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
        page_header(
            self,
            self.app,
            "Windows System Tools",
            "Manage scheduled actions and Windows applications in one place.",
        )
        self.tools_tabs = ctk.CTkTabview(
            self,
            corner_radius=14,
            fg_color=COLORS["surface"],
            segmented_button_fg_color=COLORS["surface_alt"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
        )
        self.tools_tabs.pack(
            fill="both", expand=True, padx=PAGE_PAD, pady=(0, 16)
        )

        self._tools_tab_titles = {
            "scheduler": self.app.tr("Scheduler"),
            "winget": self.app.tr("WinGet Manager"),
        }
        self.setup_scheduler_tab(self.tools_tabs.add(self._tools_tab_titles["scheduler"]))
        self.setup_winget_tab(self.tools_tabs.add(self._tools_tab_titles["winget"]))

    def setup_scheduler_tab(self, tab):
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        schedule_card = card(container)
        schedule_card.pack(fill="x")
        inner = ctk.CTkFrame(schedule_card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=16)
        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x")
        header_text = ctk.CTkFrame(header, fg_color="transparent")
        header_text.pack(side="left", fill="x", expand=True)
        section_heading(
            header_text,
            self.app,
            "Auto Shutdown Scheduler",
            "Shut down this PC automatically at the same time every day.",
        )
        ctk.CTkSwitch(
            header,
            text="Enable Daily Auto Shutdown",
            variable=self.app.opt_auto_shutdown,
            command=self.app.save_opt_settings,
            font=self.app.default_font,
        ).pack(side="right", padx=(12, 0))

        row = ctk.CTkFrame(inner, fg_color=COLORS["surface_alt"], corner_radius=10)
        row.pack(fill="x", pady=(14, 0))
        ctk.CTkLabel(
            row,
            text="Shutdown time",
            font=self.app.bold_font,
        ).pack(side="left", padx=(14, 6), pady=12)
        ctk.CTkLabel(
            row,
            text="24-hour format (HH:mm)",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(side="left", padx=(0, 12))
        self.app.entry_shutdown_time = ctk.CTkEntry(
            row,
            textvariable=self.app.opt_shutdown_time,
            width=100,
            height=36,
            font=self.app.default_font,
        )
        self.app.entry_shutdown_time.pack(side="right", padx=(8, 14), pady=10)
        ctk.CTkButton(
            row,
            text="Save & Apply",
            width=112,
            height=36,
            command=self.app.save_opt_settings,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            font=self.app.bold_font,
        ).pack(side="right", pady=10)
        ContextMenu.add_context_menu(self.app.entry_shutdown_time)
        ctk.CTkLabel(
            container,
            text="Uses Windows Task Scheduler. Disable the switch to remove the daily task.",
            font=self.app.small_font,
            text_color=COLORS["muted"],
        ).pack(anchor="w", padx=4, pady=10)

    def setup_winget_tab(self, tab):
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # A compact header makes the purpose and current state clear without
        # adding another oversized card.
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=4, pady=(0, 10))
        header_text = ctk.CTkFrame(header, fg_color="transparent")
        header_text.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            header_text,
            text="WinGet App Manager",
            font=self.app.section_font,
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_text,
            text="Search, install, and update Windows apps from one place.",
            font=self.app.default_font,
            text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(1, 0))
        self.winget_status = ctk.CTkLabel(
            header,
            text=self.app.tr("Ready"),
            width=100,
            height=28,
            corner_radius=14,
            fg_color="#24452F",
            text_color="#6BD58C",
            font=self.app.bold_font,
        )
        self.winget_status.pack(side="right", padx=(12, 0))

        actions_card = card(container)
        actions_card.pack(fill="x", pady=(0, 10))
        actions_card.grid_columnconfigure(0, weight=2, uniform="winget_actions")
        actions_card.grid_columnconfigure(1, weight=1, uniform="winget_actions")

        search_group = ctk.CTkFrame(actions_card, fg_color="transparent")
        search_group.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=(14, 10))
        ctk.CTkLabel(search_group, text="Search Packages", font=self.app.bold_font).pack(anchor="w")
        search_row = ctk.CTkFrame(search_group, fg_color="transparent")
        search_row.pack(fill="x", pady=(6, 0))
        self.winget_search_entry = ctk.CTkEntry(
            search_row,
            height=40,
            placeholder_text="e.g. vscode, discord, chrome",
            font=self.app.default_font,
        )
        self.winget_search_entry.pack(side="left", fill="x", expand=True)
        self.winget_search_btn = ctk.CTkButton(
            search_row,
            text="Search",
            width=92,
            height=40,
            command=self.run_winget_search,
            font=self.app.bold_font,
        )
        self.winget_search_btn.pack(side="left", padx=(8, 0))

        update_group = ctk.CTkFrame(actions_card, fg_color="transparent")
        update_group.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=(14, 10))
        ctk.CTkLabel(update_group, text="Installed Apps", font=self.app.bold_font).pack(anchor="w")
        self.winget_upgrade_btn = ctk.CTkButton(
            update_group,
            text="Upgrade All",
            height=40,
            fg_color=COLORS["cyan"],
            hover_color="#138496",
            command=self.run_winget_upgrade_all,
            font=self.app.bold_font,
        )
        self.winget_upgrade_btn.pack(fill="x", pady=(6, 0))

        divider = ctk.CTkFrame(actions_card, height=1, fg_color=COLORS["border"])
        divider.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16)

        install_group = ctk.CTkFrame(actions_card, fg_color="transparent")
        install_group.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(10, 14))
        ctk.CTkLabel(
            install_group, text="Install by Package ID", width=145,
            anchor="w", font=self.app.bold_font,
        ).pack(side="left")
        self.winget_install_entry = ctk.CTkEntry(
            install_group,
            height=38,
            placeholder_text="e.g. Microsoft.VisualStudioCode",
            font=self.app.default_font,
        )
        self.winget_install_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.winget_install_btn = ctk.CTkButton(
            install_group,
            text="Install",
            width=92,
            height=38,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=self.run_winget_install,
            font=self.app.bold_font,
        )
        self.winget_install_btn.pack(side="left", padx=(8, 0))

        results_card = card(container)
        results_card.pack(fill="both", expand=True)
        results_header = ctk.CTkFrame(results_card, fg_color="transparent")
        results_header.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(results_header, text="Results", font=self.app.bold_font).pack(side="left")
        self.winget_clear_btn = ctk.CTkButton(
            results_header,
            text="Clear",
            width=70,
            height=28,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            hover_color=COLORS["surface_hover"],
            command=self.clear_winget_output,
            font=self.app.default_font,
        )
        self.winget_clear_btn.pack(side="right")

        self.winget_log = ctk.CTkTextbox(
            results_card,
            fg_color=COLORS["input"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.winget_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.winget_log.insert("1.0", self.app.tr("Ready to search or manage apps.") + "\n")
        self.winget_log.configure(state="disabled")

        ContextMenu.add_context_menu(self.winget_log)
        ContextMenu.add_context_menu(self.winget_search_entry)
        ContextMenu.add_context_menu(self.winget_install_entry)
        self.winget_search_entry.bind("<Return>", lambda _event: self.run_winget_search())
        self.winget_install_entry.bind("<Return>", lambda _event: self.run_winget_install())

        self._winget_action_buttons = (
            self.winget_search_btn,
            self.winget_upgrade_btn,
            self.winget_install_btn,
        )
        self._winget_running = False
        if not self._find_winget():
            self._set_winget_state(False, "WinGet unavailable", "error")

    def run_winget_search(self):
        query = self.winget_search_entry.get().strip()
        if not query: return
        self._run_winget_cmd([
            "winget", "search", "--query", query, "--accept-source-agreements"
        ])

    def run_winget_upgrade_all(self):
        self._run_winget_cmd([
            "winget", "upgrade", "--all", "--silent",
            "--accept-package-agreements", "--accept-source-agreements",
        ])

    def run_winget_install(self):
        pkg_id = self.winget_install_entry.get().strip()
        if not pkg_id: return
        self._run_winget_cmd([
            "winget", "install", "--id", pkg_id, "--exact", "--silent",
            "--accept-package-agreements", "--accept-source-agreements",
        ])

    def _run_winget_cmd(self, command):
        if self._winget_running:
            return
        winget_path = self._find_winget()
        if not winget_path:
            self.clear_winget_output()
            self._append_winget_log(self.app.tr("WinGet is not installed or available in PATH.") + "\n")
            self._set_winget_state(False, "WinGet unavailable", "error")
            return

        command = [winget_path, *command[1:]]
        command_display = subprocess.list2cmdline(["winget", *command[1:]])
        self.winget_log.configure(state="normal")
        self.winget_log.delete("1.0", "end")
        self.winget_log.insert("end", f"> {command_display}\n\n")
        self.winget_log.configure(state="disabled")
        self._set_winget_state(True, "Running", "running")

        def _task():
            creation_flags = 0x08000000 if os.name == "nt" else 0
            try:
                process = subprocess.Popen(
                    command,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=creation_flags,
                )
                batch = []
                for line in process.stdout:
                    batch.append(line)
                    if len(batch) >= 10:
                        chunk = "".join(batch)
                        batch.clear()
                        self.app.after(0, lambda output=chunk: self._append_winget_log(output))
                if batch:
                    chunk = "".join(batch)
                    self.app.after(0, lambda output=chunk: self._append_winget_log(output))
                return_code = process.wait()
                self.app.after(0, lambda code=return_code: self._finish_winget_command(code))
            except Exception as error:
                message = str(error)
                self.app.after(0, lambda text=message: self._fail_winget_command(text))

        threading.Thread(target=_task, daemon=True).start()

    @staticmethod
    def _find_winget():
        """Locate WinGet through PATH or its standard Windows app alias."""
        discovered = shutil.which("winget")
        if discovered:
            return discovered
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            alias_path = os.path.join(
                local_app_data, "Microsoft", "WindowsApps", "winget.exe"
            )
            if os.path.isfile(alias_path):
                return alias_path
        return None

    def _set_winget_state(self, running, text, style):
        self._winget_running = running
        palette = {
            "ready": ("#24452F", "#6BD58C"),
            "running": ("#153C5C", "#6CB6FF"),
            "error": ("#542B2B", "#FF7B72"),
        }
        background, foreground = palette.get(style, palette["ready"])
        self.winget_status.configure(
            text=self.app.tr(text), fg_color=background, text_color=foreground
        )
        state = "disabled" if running else "normal"
        for button in getattr(self, "_winget_action_buttons", ()):
            button.configure(state=state)

    def _finish_winget_command(self, return_code):
        if return_code == 0:
            self._append_winget_log("\n" + self.app.tr("Command completed successfully.") + "\n")
            self._set_winget_state(False, "Completed", "ready")
        else:
            self._append_winget_log(
                "\n" + self.app.tr("Command failed with exit code") + f" {return_code}.\n"
            )
            self._set_winget_state(False, "Error", "error")

    def _fail_winget_command(self, message):
        self._append_winget_log("\n" + self.app.tr("Error") + f": {message}\n")
        self._set_winget_state(False, "Error", "error")

    def clear_winget_output(self):
        self.winget_log.configure(state="normal")
        self.winget_log.delete("1.0", "end")
        self.winget_log.configure(state="disabled")

    def _append_winget_log(self, text):
        self.winget_log.configure(state="normal")
        self.winget_log.insert("end", text)
        self.winget_log.see("end")
        self.winget_log.configure(state="disabled")

    def apply_language(self):
        for key, english_title in (("scheduler", "Scheduler"), ("winget", "WinGet Manager")):
            current_title = self._tools_tab_titles[key]
            translated_title = self.app.tr(english_title)
            if translated_title != current_title:
                self.tools_tabs.rename(current_title, translated_title)
                self._tools_tab_titles[key] = translated_title
