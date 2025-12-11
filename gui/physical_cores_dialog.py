import customtkinter as ctk
import threading
import os
from gui.base_dialog import ScrollableDialog
from gui.theme import (
    BG_CARD, BORDER_SUBTLE, ACCENT_CYAN, ACCENT_EMERALD, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_SUCCESS, TEXT_WARNING, create_section_label
)
from utils.command_runner import CommandRunner


CPU_INFO_SCRIPT = '''
$cpu = Get-CimInstance -ClassName Win32_Processor
$result = [PSCustomObject]@{
    Name = $cpu.Name
    Manufacturer = $cpu.Manufacturer
    PhysicalCores = $cpu.NumberOfCores
    LogicalCores = $cpu.NumberOfLogicalProcessors
}
$result | ConvertTo-Json -Compress
'''


class CpuInfo:
    def __init__(self, data: dict):
        self.name = data.get("Name", "Unknown CPU")
        self.manufacturer = data.get("Manufacturer", "Unknown")
        self.physical_cores = int(data.get("PhysicalCores", 0))
        self.logical_cores = int(data.get("LogicalCores", os.cpu_count() or 0))
        
        self.manufacturer_display = self._get_manufacturer_display()
        self.tech_name = "Hyper-Threading" if "Intel" in self.manufacturer else "SMT"
        self.ht_enabled = self.logical_cores > self.physical_cores
        self.is_hybrid, self.p_cores, self.e_cores = self._detect_hybrid()
    
    def _get_manufacturer_display(self) -> str:
        if "Intel" in self.manufacturer:
            return "Intel"
        elif "AMD" in self.manufacturer:
            return "AMD"
        return self.manufacturer
    
    def _detect_hybrid(self) -> tuple:
        if self.manufacturer_display != "Intel":
            return False, 0, 0
        
        gen_indicators = ["12", "13", "14", "Core Ultra"]
        is_hybrid = any(ind in self.name for ind in gen_indicators)
        
        if not is_hybrid or self.physical_cores <= 0:
            return False, 0, 0
        
        if self.ht_enabled:
            p_cores = self.logical_cores - self.physical_cores
            e_cores = 2 * self.physical_cores - self.logical_cores
        else:
            p_cores = self.physical_cores - (self.logical_cores - self.physical_cores)
            e_cores = self.logical_cores - p_cores
        
        if p_cores <= 0 or e_cores <= 0:
            return False, 0, 0
        
        return True, p_cores, e_cores


class PhysicalCoresDialog(ScrollableDialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="CPU Core Inspector",
            header_text="CPU Core Information",
            geometry="580x520",
            accent_color=ACCENT_CYAN
        )
        self._load_cpu_info()
    
    def _show_loading(self, message: str = "Analyzing CPU...") -> None:
        super()._show_loading(message)
    
    def _load_cpu_info(self) -> None:
        threading.Thread(target=self._fetch_cpu_info, daemon=True).start()
    
    def _fetch_cpu_info(self) -> None:
        try:
            data = CommandRunner.run_powershell_json(CPU_INFO_SCRIPT)
            if data:
                cpu_info = CpuInfo(data[0])
                self.after(0, lambda: self._display_info(cpu_info))
            else:
                self.after(0, lambda: self._display_error("No CPU data found"))
        except Exception as e:
            self.after(0, lambda: self._display_error(str(e)))
    
    def _display_info(self, cpu: CpuInfo) -> None:
        self._clear_scroll_frame()
        
        self._create_processor_section(cpu)
        self._create_config_section(cpu)
        self._create_core_map_section(cpu)
    
    def _create_processor_section(self, cpu: CpuInfo) -> None:
        create_section_label(self.scroll_frame, "Processor").pack(anchor="w", padx=12, pady=(15, 10))
        
        info_card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=10,
            border_color=BORDER_SUBTLE, border_width=1
        )
        info_card.pack(fill="x", padx=12, pady=(0, 5))
        
        ctk.CTkLabel(
            info_card, text=cpu.name,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=TEXT_PRIMARY, wraplength=420
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        ctk.CTkLabel(
            info_card, text=f"Manufacturer: {cpu.manufacturer_display}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_SECONDARY
        ).pack(anchor="w", padx=15, pady=(0, 12))
    
    def _create_config_section(self, cpu: CpuInfo) -> None:
        create_section_label(self.scroll_frame, "Core Configuration").pack(anchor="w", padx=12, pady=(20, 10))
        
        config_card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=10,
            border_color=BORDER_SUBTLE, border_width=1
        )
        config_card.pack(fill="x", padx=12, pady=(0, 5))
        
        ht_status = "Enabled" if cpu.ht_enabled else "Disabled"
        rows = [
            ("Physical Cores", str(cpu.physical_cores)),
            ("Logical Processors", str(cpu.logical_cores)),
            (cpu.tech_name, ht_status),
        ]
        if cpu.is_hybrid:
            rows.extend([
                ("Hybrid Architecture", "Yes"),
                ("P-Cores (Performance)", str(cpu.p_cores)),
                ("E-Cores (Efficiency)", str(cpu.e_cores))
            ])
        
        for label, value in rows:
            self._create_info_row(config_card, label, value)
    
    def _create_info_row(self, parent, label: str, value: str) -> None:
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", padx=15, pady=6)
        
        ctk.CTkLabel(
            row_frame, text=label,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_SECONDARY
        ).pack(side="left")
        
        value_color = TEXT_SUCCESS if value in ["Enabled", "Yes"] else TEXT_PRIMARY
        ctk.CTkLabel(
            row_frame, text=value,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=value_color
        ).pack(side="right")
    
    def _create_core_map_section(self, cpu: CpuInfo) -> None:
        create_section_label(self.scroll_frame, "Logical Processor Map").pack(anchor="w", padx=12, pady=(20, 10))
        
        map_card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=10,
            border_color=BORDER_SUBTLE, border_width=1
        )
        map_card.pack(fill="x", padx=12, pady=(0, 5))
        
        core_frame = ctk.CTkFrame(map_card, fg_color="transparent")
        core_frame.pack(fill="x", padx=15, pady=15)
        
        ht_status = "Enabled" if cpu.ht_enabled else "Disabled"
        cols = 8
        
        for i in range(cpu.logical_cores):
            color, label = self._get_core_color_label(cpu, i, ht_status)
            
            core_btn = ctk.CTkButton(
                core_frame, text=f"{i}\n{label}", width=44, height=44,
                fg_color=color, hover_color=color, text_color="#ffffff",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                corner_radius=6
            )
            core_btn.grid(row=i // cols, column=i % cols, padx=3, pady=3)
        
        self._create_legend(map_card, cpu, ht_status)
    
    def _get_core_color_label(self, cpu: CpuInfo, index: int, ht_status: str) -> tuple:
        if cpu.is_hybrid:
            p_end = cpu.p_cores * 2 - 1 if ht_status == "Enabled" else cpu.p_cores - 1
            if index <= p_end:
                if ht_status == "Enabled" and index % 2 == 1:
                    return TEXT_WARNING, "PT"
                return ACCENT_CYAN, "P"
            return ACCENT_EMERALD, "E"
        else:
            if ht_status == "Enabled" and index % 2 == 1:
                return TEXT_WARNING, "T"
            return ACCENT_CYAN, "C"
    
    def _create_legend(self, parent, cpu: CpuInfo, ht_status: str) -> None:
        legend_frame = ctk.CTkFrame(parent, fg_color="transparent")
        legend_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        if cpu.is_hybrid:
            legends = [(ACCENT_CYAN, "P-Core"), (TEXT_WARNING, "P-Thread"), (ACCENT_EMERALD, "E-Core")]
        elif ht_status == "Enabled":
            legends = [(ACCENT_CYAN, "Core"), (TEXT_WARNING, "Thread")]
        else:
            legends = [(ACCENT_CYAN, "Core")]
        
        for color, text in legends:
            leg = ctk.CTkFrame(legend_frame, fg_color="transparent")
            leg.pack(side="left", padx=(0, 20))
            ctk.CTkFrame(leg, fg_color=color, width=14, height=14, corner_radius=3).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(leg, text=text, font=ctk.CTkFont(family="Segoe UI", size=11), text_color=TEXT_SECONDARY).pack(side="left")


def show_physical_cores_dialog(parent) -> None:
    dialog = PhysicalCoresDialog(parent)
    dialog.wait_window()