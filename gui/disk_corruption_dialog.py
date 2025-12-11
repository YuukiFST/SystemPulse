import customtkinter as ctk
import threading
import os
import shutil
import subprocess
from gui.base_dialog import BaseDialog
from gui.theme import (
    BG_VOID, BG_SURFACE, BG_CARD, BG_ELEVATED, BORDER_SUBTLE, ACCENT_CYAN,
    ACCENT_EMERALD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_SUCCESS, AccentButton
)
from utils.command_runner import CommandRunner


REPAIR_COMMANDS = [
    ("chkdsk C: /scan", "Quick Disk Check (C:)"),
    ("dism /Online /Cleanup-Image /CheckHealth", "DISM CheckHealth"),
    ("dism /Online /Cleanup-Image /ScanHealth", "DISM ScanHealth"),
    ("dism /Online /Cleanup-Image /RestoreHealth", "DISM RestoreHealth"),
    ("dism /Online /Cleanup-Image /AnalyzeComponentStore", "DISM AnalyzeComponentStore"),
    ("dism /Online /Cleanup-Image /StartComponentCleanup", "DISM StartComponentCleanup"),
    ("sfc /scannow", "System File Checker (SFC)"),
    ("cleanmgr /sagerun:1", "Disk Cleanup"),
    ("ipconfig /flushdns", "Flushing DNS Cache"),
]


class DiskCorruptionDialog(BaseDialog):
    def __init__(self, parent):
        self._repair_running = False
        super().__init__(
            parent,
            title="Disk Health Scan",
            geometry="750x550",
            resizable=(False, False)
        )
        self.after(500, self._start_repair_process)
    
    def _can_close(self) -> bool:
        return not self._repair_running
    
    def _build_ui(self) -> None:
        self._build_header()
        self._build_log_area()
        self._build_footer()
    
    def _build_header(self) -> None:
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(25, 15))
        
        ctk.CTkLabel(
            header_frame, text="System Repair & Optimization",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Running system integrity checks, disk repairs, and cleanup operations...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
    
    def _build_log_area(self) -> None:
        log_container = ctk.CTkFrame(
            self, fg_color=BG_CARD, corner_radius=12,
            border_color=BORDER_SUBTLE, border_width=1
        )
        log_container.pack(fill="both", expand=True, padx=25, pady=(0, 15))
        
        self._log_box = ctk.CTkTextbox(
            log_container,
            font=ctk.CTkFont(family="Cascadia Code", size=11),
            fg_color=BG_SURFACE, text_color=TEXT_PRIMARY,
            border_width=0, corner_radius=8
        )
        self._log_box.pack(fill="both", expand=True, padx=10, pady=10)
        self._log_box.configure(state="disabled")
    
    def _build_footer(self) -> None:
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        self._status_label = ctk.CTkLabel(
            footer_frame, text="⏳ Initializing...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=ACCENT_CYAN
        )
        self._status_label.pack(side="left")
        
        self._close_btn = AccentButton(
            footer_frame, text="Close", accent=ACCENT_EMERALD,
            command=self.destroy
        )
        self._close_btn.configure(state="disabled", fg_color=BG_ELEVATED)
        self._close_btn.pack(side="right")
    
    def _log(self, message: str) -> None:
        def _update():
            if self._is_destroyed:
                return
            try:
                self._log_box.configure(state="normal")
                self._log_box.insert("end", message + "\n")
                self._log_box.see("end")
                self._log_box.configure(state="disabled")
            except (RuntimeError, AttributeError):
                pass
        self.after(0, _update)
    
    def _update_status(self, text: str, color: str = None) -> None:
        def _update():
            if self._is_destroyed:
                return
            try:
                self._status_label.configure(text=text)
                if color:
                    self._status_label.configure(text_color=color)
            except (RuntimeError, AttributeError):
                pass
        self.after(0, _update)
    
    def _run_command(self, command: str, description: str) -> None:
        self._update_status(f"⚙ Running: {description}...")
        self._log(f"\n━━━ {description} ━━━")
        
        try:
            CommandRunner.run_shell_streaming(
                command,
                on_output=lambda line: self._log(line),
                on_complete=lambda code: self._log(
                    "✓ Completed successfully." if code == 0 else f"⚠ Completed with exit code {code}."
                )
            )
        except (subprocess.SubprocessError, OSError) as e:
            self._log(f"✗ Error executing command: {e}")
    
    def _start_repair_process(self) -> None:
        self._repair_running = True
        threading.Thread(target=self._repair_thread, daemon=True).start()
    
    def _repair_thread(self) -> None:
        for command, description in REPAIR_COMMANDS:
            self._run_command(command, description)
        
        self._grant_temp_permissions()
        self._clear_event_logs()
        self._clean_temp_files()
        
        self._update_status("✓ All operations completed successfully!", TEXT_SUCCESS)
        self._log("\n━━━ DONE ━━━")
        self._repair_running = False
        self._enable_close_button()
    
    def _grant_temp_permissions(self) -> None:
        temp_paths = [
            os.environ.get("TEMP", ""),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Temp"),
            "C:\\Windows\\Temp",
            "C:\\Windows\\Prefetch"
        ]
        
        for path in temp_paths:
            if path:
                self._run_command(
                    f'icacls "{path}" /grant Everyone:(OI)(CI)F /T',
                    f"Granting Permissions to {os.path.basename(path) or 'TEMP'}"
                )
    
    def _clear_event_logs(self) -> None:
        self._update_status("⚙ Clearing Event Logs...")
        self._log("\n━━━ Clearing Event Logs ━━━")
        try:
            CommandRunner.run_shell(
                'for /f "tokens=*" %a in (\'wevtutil el\') do wevtutil cl "%a"'
            )
            self._log("✓ Event logs cleared.")
        except (subprocess.SubprocessError, OSError) as e:
            self._log(f"✗ Error clearing logs: {e}")
    
    def _clean_temp_files(self) -> None:
        self._update_status("⚙ Cleaning Temporary Files...")
        self._log("\n━━━ Cleaning Temporary Files ━━━")
        
        folders = [
            os.environ.get("TEMP", ""),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Temp"),
            "C:\\Windows\\Temp",
            "C:\\Windows\\Prefetch"
        ]
        
        for folder in folders:
            if not folder or not os.path.exists(folder):
                continue
            try:
                self._clean_folder(folder)
                self._log(f"✓ Cleaned: {folder}")
            except (IOError, OSError, shutil.Error) as e:
                self._log(f"✗ Error cleaning {folder}: {e}")
    
    def _clean_folder(self, folder: str) -> None:
        for root, dirs, files in os.walk(folder):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except (IOError, OSError, PermissionError):
                    pass
            for d in dirs:
                try:
                    shutil.rmtree(os.path.join(root, d))
                except (IOError, OSError, shutil.Error, PermissionError):
                    pass
    
    def _enable_close_button(self) -> None:
        def _update():
            if self._is_destroyed:
                return
            try:
                self._close_btn.configure(state="normal", fg_color=ACCENT_EMERALD)
            except (RuntimeError, AttributeError):
                pass
        self.after(0, _update)


def show_disk_corruption_dialog(parent) -> None:
    DiskCorruptionDialog(parent)