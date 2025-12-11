import customtkinter as ctk
import threading
from gui.base_dialog import ScrollableDialog
from gui.theme import (
    BG_CARD, BG_HOVER, BORDER_SUBTLE, ACCENT_PURPLE, TEXT_PRIMARY,
    TEXT_MUTED, TEXT_SUCCESS, GlowButton, create_section_label
)
from utils.command_runner import CommandRunner


DRIVER_REGISTRY_SCRIPT = '''
$results = @()
$classes = @("Win32_VideoController", "Win32_NetworkAdapter")
foreach ($class in $classes) {
    $devices = Get-CimInstance -ClassName $class | Where-Object { $_.PNPDeviceID -like "PCI\\VEN_*" }
    foreach ($device in $devices) {
        $deviceId = $device.PNPDeviceID
        $regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\$deviceId"
        try {
            $driverValue = Get-ItemProperty -Path $regPath -Name "Driver" -ErrorAction Stop
            $driverPath = $driverValue.Driver
            $results += [PSCustomObject]@{
                Class = $class
                Name = $device.Name
                Path = "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\$driverPath"
            }
        } catch { }
    }
}
$results | ConvertTo-Json -Compress
'''


class DriverRegistryKeysDialog(ScrollableDialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Driver Registry Viewer",
            header_text="Driver Registry Viewer",
            geometry="700x480",
            accent_color=ACCENT_PURPLE
        )
        self._status_label = None
        self._load_drivers()
    
    def _build_header_extra(self, header: ctk.CTkFrame) -> None:
        ctk.CTkLabel(
            header, text="Click path to copy",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED
        ).pack(side="right")
    
    def _build_footer_left(self, footer: ctk.CTkFrame) -> None:
        GlowButton(
            footer, text="Refresh", command=self._load_drivers,
            accent=ACCENT_PURPLE
        ).pack(side="left")
        
        self._status_label = ctk.CTkLabel(
            footer, text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SUCCESS
        )
        self._status_label.pack(side="left", padx=20)
    
    def _show_loading(self, message: str = "Loading drivers...") -> None:
        super()._show_loading(message)
    
    def _load_drivers(self) -> None:
        self._clear_scroll_frame()
        self._show_loading()
        threading.Thread(target=self._fetch_drivers, daemon=True).start()
    
    def _fetch_drivers(self) -> None:
        try:
            drivers = CommandRunner.run_powershell_json(DRIVER_REGISTRY_SCRIPT)
            self.after(0, lambda: self._display_drivers(drivers or []))
        except Exception as e:
            self.after(0, lambda: self._display_error(str(e)))
    
    def _display_drivers(self, drivers: list) -> None:
        self._clear_scroll_frame()
        
        if not drivers:
            ctk.CTkLabel(
                self.scroll_frame, text="No drivers found",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_MUTED
            ).pack(pady=40)
            return
        
        gpu_drivers = [d for d in drivers if d.get("Class") == "Win32_VideoController"]
        net_drivers = [d for d in drivers if d.get("Class") == "Win32_NetworkAdapter"]
        
        if gpu_drivers:
            self._add_section("GPU Drivers", gpu_drivers)
        if net_drivers:
            self._add_section("Network Adapters", net_drivers)
    
    def _add_section(self, title: str, drivers: list) -> None:
        create_section_label(self.scroll_frame, title).pack(anchor="w", padx=12, pady=(20, 10))
        
        for driver in drivers:
            self._create_driver_card(driver)
    
    def _create_driver_card(self, driver: dict) -> None:
        card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=10,
            border_color=BORDER_SUBTLE, border_width=1
        )
        card.pack(fill="x", padx=12, pady=4)
        
        ctk.CTkLabel(
            card, text=driver.get("Name", "Unknown"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=15, pady=(12, 4))
        
        path = driver.get("Path", "")
        path_btn = ctk.CTkButton(
            card, text=path,
            font=ctk.CTkFont(family="Cascadia Code", size=10),
            fg_color="transparent", hover_color=BG_HOVER,
            text_color=ACCENT_PURPLE, anchor="w",
            height=24, corner_radius=4,
            command=lambda p=path: self._copy_path(p)
        )
        path_btn.pack(anchor="w", padx=10, pady=(0, 12), fill="x")
    
    def _copy_path(self, path: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(path)
        if self._status_label:
            self._status_label.configure(text="✓ Copied to clipboard")
            self.after(2000, lambda: self._status_label.configure(text=""))


def show_driver_registry_keys_dialog(parent) -> None:
    dialog = DriverRegistryKeysDialog(parent)
    dialog.wait_window()
