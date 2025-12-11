import customtkinter as ctk
import threading
from gui.base_dialog import ScrollableDialog
from gui.theme import (
    BG_CARD, BORDER_SUBTLE, ACCENT_PINK, ACCENT_EMERALD, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_MUTED, TEXT_SUCCESS, TEXT_WARNING, TEXT_ERROR,
    GlowButton, create_section_label
)
from utils.command_runner import CommandRunner


SERVICE_DEPENDENCY_SCRIPT = '''
$errors = @()
$services = Get-WmiObject -Class Win32_Service
foreach ($service in $services) {
    if ($service.StartMode -ne "Disabled") { continue }
    $dependentServices = Get-Service -Name $service.Name -DependentServices -ErrorAction SilentlyContinue
    foreach ($dep in $dependentServices) {
        $startValue = (Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\$($dep.Name)" -ErrorAction SilentlyContinue).Start
        if ($startValue -ne 4) {
            $errors += [PSCustomObject]@{
                DependentService = $dep.Name
                DependentDisplayName = $dep.DisplayName
                DependentStartType = $startValue
                DisabledService = $service.Name
                DisabledDisplayName = $service.DisplayName
            }
        }
    }
}
$errors | ConvertTo-Json -Compress
'''

START_TYPE_NAMES = {0: "Boot", 1: "System", 2: "Automatic", 3: "Manual", 4: "Disabled"}


class ServiceDependencyDialog(ScrollableDialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Dependency Map",
            header_text="Dependency Map",
            geometry="700x500",
            accent_color=ACCENT_PINK
        )
        self._status_label = None
        self._check_dependencies()
    
    def _build_header_extra(self, header: ctk.CTkFrame) -> None:
        self._status_label = ctk.CTkLabel(
            header, text="Checking...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED
        )
        self._status_label.pack(side="right")
    
    def _build_content_area(self) -> None:
        info_frame = ctk.CTkFrame(
            self, fg_color=BG_CARD, corner_radius=10,
            border_color=BORDER_SUBTLE, border_width=1
        )
        info_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            info_frame,
            text="This tool checks for services that depend on disabled services.\n"
                 "Such dependencies can cause system errors or prevent services from starting.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_SECONDARY, justify="left"
        ).pack(anchor="w", padx=15, pady=12)
        
        super()._build_content_area()
    
    def _build_footer_left(self, footer: ctk.CTkFrame) -> None:
        GlowButton(
            footer, text="Refresh", command=self._check_dependencies,
            accent=ACCENT_PINK
        ).pack(side="left")
    
    def _show_loading(self, message: str = "Analyzing service dependencies...") -> None:
        super()._show_loading(message)
    
    def _check_dependencies(self) -> None:
        self._clear_scroll_frame()
        self._show_loading()
        if self._status_label:
            self._status_label.configure(text="Checking...", text_color=TEXT_MUTED)
        threading.Thread(target=self._analyze_dependencies, daemon=True).start()
    
    def _analyze_dependencies(self) -> None:
        try:
            errors = CommandRunner.run_powershell_json(SERVICE_DEPENDENCY_SCRIPT, timeout=60)
            self.after(0, lambda: self._display_results(errors or []))
        except Exception as e:
            self.after(0, lambda: self._display_error(str(e)))
    
    def _display_results(self, errors: list) -> None:
        self._clear_scroll_frame()
        
        if not errors:
            self._display_success()
            return
        
        self._display_errors(errors)
    
    def _display_success(self) -> None:
        success_frame = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=12,
            border_color=ACCENT_EMERALD, border_width=2
        )
        success_frame.pack(fill="x", padx=12, pady=30)
        
        ctk.CTkLabel(
            success_frame, text="✓",
            font=ctk.CTkFont(size=40),
            text_color=ACCENT_EMERALD
        ).pack(pady=(20, 8))
        
        ctk.CTkLabel(
            success_frame, text="No Dependency Errors Found",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=ACCENT_EMERALD
        ).pack()
        
        ctk.CTkLabel(
            success_frame, text="All service dependencies are properly configured.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_SECONDARY
        ).pack(pady=(8, 20))
        
        if self._status_label:
            self._status_label.configure(text="✓ No errors", text_color=TEXT_SUCCESS)
    
    def _display_errors(self, errors: list) -> None:
        if self._status_label:
            self._status_label.configure(text=f"⚠ {len(errors)} error(s) found", text_color=TEXT_ERROR)
        
        create_section_label(self.scroll_frame, "Dependency Errors").pack(anchor="w", padx=12, pady=(15, 10))
        
        for error in errors:
            self._create_error_card(error)
    
    def _create_error_card(self, error: dict) -> None:
        card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=10,
            border_color=TEXT_WARNING, border_width=1
        )
        card.pack(fill="x", padx=12, pady=4)
        
        dep_name = error.get("DependentDisplayName") or error.get("DependentService", "Unknown")
        disabled_name = error.get("DisabledDisplayName") or error.get("DisabledService", "Unknown")
        start_type = START_TYPE_NAMES.get(error.get("DependentStartType", -1), "Unknown")
        
        ctk.CTkLabel(
            card, text=f"⚠  {dep_name}",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_WARNING
        ).pack(anchor="w", padx=15, pady=(12, 4))
        
        ctk.CTkLabel(
            card, text=f"Start Type: {start_type}  •  Depends on: {disabled_name} (Disabled)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", padx=15, pady=(0, 12))
    
    def _display_error(self, error: str) -> None:
        super()._display_error(error)
        if self._status_label:
            self._status_label.configure(text="Error", text_color=TEXT_ERROR)


def show_service_dependency_dialog(parent) -> None:
    dialog = ServiceDependencyDialog(parent)
    dialog.wait_window()
