import customtkinter as ctk
import threading
import winreg
import re
import subprocess
import pythoncom
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from gui.base_dialog import ScrollableDialog
from gui.theme import (
    BG_CARD, BG_ELEVATED, BORDER_SUBTLE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_EMERALD,
    ACCENT_PINK, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, TEXT_SUCCESS, TEXT_WARNING,
    TEXT_ERROR, GlowButton, create_section_label, BG_VOID, BG_SURFACE, interpolate_color
)


USB_CONTROLLER_DATABASE = {
    ("8086", "A36D"): ("Intel C620 Series xHCI Controller", "Intel C620 Chipset", 1),
    ("8086", "9D2F"): ("Intel Sunrise Point-LP xHCI Controller", "Intel 100 Series (6th Gen)", 1),
    ("8086", "A12F"): ("Intel Sunrise Point xHCI Controller", "Intel 100 Series (6th Gen)", 1),
    ("8086", "8D31"): ("Intel C610/X99 xHCI Controller", "Intel X99/C610 HEDT", 1),
    ("8086", "8CB1"): ("Intel 9 Series xHCI Controller", "Intel 9 Series (5th Gen)", 1),
    ("8086", "8C31"): ("Intel 8 Series xHCI Controller", "Intel 8 Series (4th Gen)", 1),
    ("8086", "1E31"): ("Intel 7 Series xHCI Controller", "Intel 7 Series (3rd Gen)", 1),
    ("8086", "A2AF"): ("Intel Union Point xHCI Controller", "Intel 200 Series (7th Gen)", 1),
    ("8086", "A3AF"): ("Intel Comet Lake xHCI Controller", "Intel 400 Series (10th Gen)", 1),
    ("8086", "43ED"): ("Intel Tiger Lake xHCI Controller", "Intel 500 Series (11th Gen)", 1),
    ("8086", "7AE0"): ("Intel Alder Lake xHCI Controller", "Intel 600 Series (12th Gen)", 1),
    ("8086", "51ED"): ("Intel Alder Lake-P xHCI Controller", "Intel 600 Series Mobile", 1),
    ("8086", "7A60"): ("Intel Raptor Lake xHCI Controller", "Intel 700 Series (13th Gen)", 1),
    ("8086", "460E"): ("Intel Meteor Lake xHCI Controller", "Intel (14th Gen)", 1),
    ("8086", "15B5"): ("Intel JHL6240 Thunderbolt 3 USB Controller", "Thunderbolt 3 (Alpine Ridge)", 2),
    ("8086", "15B6"): ("Intel JHL6240 Thunderbolt 3 USB Controller", "Thunderbolt 3 (Alpine Ridge)", 2),
    ("8086", "15D2"): ("Intel JHL6540 Thunderbolt 3 USB Controller", "Thunderbolt 3 (Alpine Ridge)", 2),
    ("8086", "15D4"): ("Intel JHL6540 Thunderbolt 3 USB Controller", "Thunderbolt 3 (Alpine Ridge)", 2),
    ("8086", "15E9"): ("Intel JHL7540 Thunderbolt 3 USB Controller", "Thunderbolt 3 (Titan Ridge)", 2),
    ("8086", "15EC"): ("Intel JHL7540 Thunderbolt 3 USB Controller", "Thunderbolt 3 (Titan Ridge)", 2),
    ("8086", "9A13"): ("Intel Tiger Lake Thunderbolt 4 USB Controller", "Thunderbolt 4 (Tiger Lake)", 2),
    ("8086", "9A1B"): ("Intel Tiger Lake Thunderbolt 4 USB Controller", "Thunderbolt 4 (Tiger Lake)", 2),
    ("8086", "463E"): ("Intel Alder Lake Thunderbolt 4 USB Controller", "Thunderbolt 4 (Alder Lake)", 2),
    ("8086", "466D"): ("Intel Alder Lake Thunderbolt 4 USB Controller", "Thunderbolt 4 (Alder Lake)", 2),
    ("8086", "A74D"): ("Intel Raptor Lake Thunderbolt 4 USB Controller", "Thunderbolt 4 (Raptor Lake)", 2),
    ("8086", "A76D"): ("Intel Raptor Lake Thunderbolt 4 USB Controller", "Thunderbolt 4 (Raptor Lake)", 2),
    ("1022", "43D5"): ("AMD X570 USB 3.1 XHCI Controller", "X570 Chipset (AM4)", 1),
    ("1022", "43EE"): ("500 Series Chipset USB 3.1 XHCI Controller", "X570/B550 (AM4)", 1),
    ("1022", "149C"): ("Matisse USB 3.0 Host Controller", "Ryzen 3000/5000 Desktop (Zen 2/3)", 0),
    ("1022", "145F"): ("Zeppelin USB 3.0 Host Controller", "Ryzen 1000/2000 Desktop (Zen/Zen+)", 0),
    ("1022", "1639"): ("Renoir/Cezanne USB 3.1 Host Controller", "Ryzen 4000/5000 Mobile (Zen 2/3)", 0),
    ("1022", "15E0"): ("Raven/Raven2 USB 3.1 Host Controller", "Ryzen 2000/3000 APU (Zen/Zen+)", 0),
    ("1022", "15E1"): ("Raven/Raven2 USB 3.1 Host Controller", "Ryzen 2000/3000 APU (Zen/Zen+)", 0),
    ("1022", "43D0"): ("AMD X399 USB 3.1 XHCI Controller", "X399 Chipset (TR4)", 1),
    ("1022", "43B9"): ("AMD X370 USB 3.1 XHCI Controller", "X370/B350 (AM4)", 1),
    ("1022", "43BB"): ("AMD 300 Series USB 3.1 XHCI Controller", "A320/B350/X370 (AM4)", 1),
    ("1022", "43BC"): ("AMD FCH USB 3.1 XHCI Controller", "AMD FCH", 1),
    ("1022", "43E7"): ("AMD 600 Series USB XHCI Controller", "X670/B650 (AM5)", 1),
    ("1022", "161D"): ("Rembrandt USB 3.1 Host Controller", "Ryzen 6000/7000 Mobile (Zen 3+)", 0),
    ("1022", "161E"): ("Rembrandt USB 3.1 Host Controller", "Ryzen 6000/7000 Mobile (Zen 3+)", 0),
    ("1022", "161F"): ("Rembrandt USB 3.1 Host Controller", "Ryzen 6000/7000 Mobile (Zen 3+)", 0),
    ("1022", "15B9"): ("Phoenix USB 3.1 Host Controller", "Ryzen 7040 Mobile (Zen 4)", 0),
    ("1B21", "1142"): ("ASMedia ASM1142 USB 3.1 Host Controller", "Third-Party Add-in Card", 1),
    ("1B21", "1242"): ("ASMedia ASM1242 USB 3.1 Host Controller", "Third-Party Add-in Card", 1),
    ("1B21", "2142"): ("ASMedia ASM2142 USB 3.1 Host Controller", "Third-Party Add-in Card", 1),
    ("1B21", "3242"): ("ASMedia ASM3242 USB 3.2 Host Controller", "Third-Party Add-in Card", 1),
    ("1B21", "1343"): ("ASMedia ASM1343 USB 3.2 Host Controller", "Third-Party Add-in Card", 1),
    ("1B73", "1100"): ("Fresco Logic FL1100 USB 3.0 Host Controller", "Third-Party Add-in Card", 1),
    ("1B73", "1009"): ("Fresco Logic FL1009 USB 3.0 Host Controller", "Third-Party Add-in Card", 1),
    ("1106", "3483"): ("VIA VL805 USB 3.0 Host Controller", "Third-Party (Raspberry Pi 4)", 1),
    ("1106", "3038"): ("VIA USB UHCI Controller", "Legacy VIA Chipset", 1),
    ("104C", "8241"): ("Texas Instruments USB 3.0 Host Controller", "Third-Party Add-in Card", 1),
    ("10DE", "1ADA"): ("NVIDIA USB 3.0 Host Controller", "NVIDIA nForce", 1),
    ("10DE", "1ADB"): ("NVIDIA USB-C Controller", "NVIDIA GPU USB-C", 2),
}

KNOWN_DEVICES = {
    ("1532", "00B2"): ("Razer DeathAdder V3", "mouse"),
    ("1532", "00A4"): ("Razer DeathAdder V2", "mouse"),
    ("1532", "005C"): ("Razer DeathAdder Elite", "mouse"),
    ("046D", "C539"): ("Logitech G Pro Wireless", "mouse"),
    ("046D", "C547"): ("Logitech G502 X Plus", "mouse"),
    ("3151", "4015"): ("Gaming Keyboard", "keyboard"),
}


class UsbDataFetcher:
    @staticmethod
    def get_controllers() -> List[Dict]:
        import wmi
        c = wmi.WMI()
        controllers = []
        for dev in c.Win32_PnPEntity(Status="OK"):
            if dev.PNPClass == "USB" and dev.PNPDeviceID and dev.PNPDeviceID.startswith("PCI"):
                vid, did = UsbDataFetcher._extract_vendor_device_ids(dev)
                msi = UsbDataFetcher._check_msi_enabled(dev.PNPDeviceID)
                controllers.append({
                    "Name": dev.Name or "Unknown Controller",
                    "InstanceId": dev.PNPDeviceID,
                    "VendorId": vid,
                    "DeviceId": did,
                    "MSIEnabled": msi
                })
        return controllers
    
    @staticmethod
    def _extract_vendor_device_ids(dev) -> Tuple[str, str]:
        vid = did = ""
        if dev.HardwareID:
            for hwid in dev.HardwareID:
                if "VEN_" in hwid.upper():
                    m = re.search(r'VEN_([0-9A-Fa-f]{4})', hwid, re.I)
                    if m:
                        vid = m.group(1).upper()
                if "DEV_" in hwid.upper():
                    m = re.search(r'DEV_([0-9A-Fa-f]{4})', hwid, re.I)
                    if m:
                        did = m.group(1).upper()
                if vid and did:
                    break
        return vid, did
    
    @staticmethod
    def _check_msi_enabled(pnp_device_id: str) -> bool:
        try:
            reg_path = f"SYSTEM\\CurrentControlSet\\Enum\\{pnp_device_id}\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                val, _ = winreg.QueryValueEx(key, "MSISupported")
                return val == 1
        except (FileNotFoundError, OSError, WindowsError):
            return False
    
    @staticmethod
    def get_devices() -> List[Dict]:
        import wmi
        c = wmi.WMI()
        seen_vid_pids = {}
        
        for dev in c.Win32_PnPEntity(Status="OK"):
            if not dev.Name:
                continue
            
            pnp_class = dev.PNPClass or ""
            instance_id = dev.PNPDeviceID or ""
            class_lower = pnp_class.lower()
            name = dev.Name
            
            if class_lower not in ("mouse", "keyboard", "media", "usb", "hidclass", "audioendpoint"):
                if not instance_id.upper().startswith("USB\\VID_"):
                    continue
            
            vid, pid = UsbDataFetcher._extract_vid_pid(instance_id, dev)
            if not vid or not pid:
                continue
            
            vid_pid_key = f"{vid}:{pid}"
            
            known = KNOWN_DEVICES.get((vid, pid))
            if known:
                known_name, known_type = known
                if vid_pid_key not in seen_vid_pids:
                    seen_vid_pids[vid_pid_key] = {
                        "Name": known_name,
                        "Class": known_type.capitalize(),
                        "InstanceId": instance_id,
                        "VendorId": vid,
                        "ProductId": pid,
                        "priority": 100
                    }
                continue
            
            current_priority = UsbDataFetcher._calculate_priority(class_lower, name, instance_id)
            
            if vid_pid_key in seen_vid_pids:
                if current_priority <= seen_vid_pids[vid_pid_key]["priority"]:
                    continue
            
            seen_vid_pids[vid_pid_key] = {
                "Name": name,
                "Class": pnp_class,
                "InstanceId": instance_id,
                "VendorId": vid,
                "ProductId": pid,
                "priority": current_priority
            }
        
        return [
            {"Name": d["Name"], "Class": d["Class"], "InstanceId": d["InstanceId"], 
             "VendorId": d["VendorId"], "ProductId": d["ProductId"]}
            for d in seen_vid_pids.values()
        ]
    
    @staticmethod
    def _extract_vid_pid(instance_id: str, dev) -> Tuple[str, str]:
        vid = pid = ""
        
        if "VID_" in instance_id.upper() and "PID_" in instance_id.upper():
            m_vid = re.search(r'VID_([0-9A-Fa-f]{4})', instance_id, re.I)
            m_pid = re.search(r'PID_([0-9A-Fa-f]{4})', instance_id, re.I)
            if m_vid:
                vid = m_vid.group(1).upper()
            if m_pid:
                pid = m_pid.group(1).upper()
        
        if (not vid or not pid) and dev.HardwareID:
            for hwid in dev.HardwareID:
                m_vid = re.search(r'VID_([0-9A-Fa-f]{4})', hwid, re.I)
                m_pid = re.search(r'PID_([0-9A-Fa-f]{4})', hwid, re.I)
                if m_vid:
                    vid = m_vid.group(1).upper()
                if m_pid:
                    pid = m_pid.group(1).upper()
                if vid and pid:
                    break
        
        return vid, pid
    
    @staticmethod
    def _calculate_priority(class_lower: str, name: str, instance_id: str) -> int:
        name_lower = name.lower()
        is_mouse_name = any(x in name_lower for x in ("mouse", "razer", "deathadder", "logitech g", "glorious"))
        is_keyboard_name = "keyboard" in name_lower
        is_audio_name = "audio" in name_lower
        
        if class_lower == "media" and is_audio_name:
            return 12
        if class_lower == "mouse" and is_mouse_name:
            return 10
        if class_lower == "keyboard" and is_keyboard_name:
            return 10
        if class_lower == "mouse":
            return 7
        if class_lower == "keyboard":
            return 6
        if class_lower == "media":
            return 5
        if class_lower == "usb" and ("composite" in name_lower or instance_id.upper().startswith("USB\\VID_")):
            return 4
        return 1
    
    @staticmethod
    def get_selective_suspend() -> Dict:
        try:
            result = subprocess.run(
                ["powercfg", "/query", "SCHEME_CURRENT", "2a737441-1930-4402-8d77-b2bebba308a3", "48e6b7a6-50f5-4782-a5d4-53bb8f07e226"],
                capture_output=True, text=True, timeout=5
            )
            ac_val = dc_val = ""
            for line in result.stdout.split('\n'):
                if "Current AC Power Setting Index:" in line:
                    ac_val = line.split("0x")[-1].strip() if "0x" in line else ""
                elif "Current DC Power Setting Index:" in line:
                    dc_val = line.split("0x")[-1].strip() if "0x" in line else ""
            return {"ACValue": ac_val, "DCValue": dc_val}
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            return {}


@dataclass
class PathStyle:
    color: str
    label: str
    visual: str
    bg_tint: str


class UsbControllerInfo:
    def __init__(self, data: dict):
        self.name = data.get("Name", "Unknown Controller")
        self.instance_id = data.get("InstanceId", "")
        self.vendor_id = str(data.get("VendorId", "")).upper()
        self.device_id = str(data.get("DeviceId", "")).upper()
        self.msi_enabled = data.get("MSIEnabled", False)
        self.devices: List["UsbDeviceInfo"] = []
        
        db_entry = USB_CONTROLLER_DATABASE.get((self.vendor_id, self.device_id))
        if db_entry:
            self.db_name, self.platform_info, self.chip_count = db_entry
        else:
            self.db_name = self.name
            self.platform_info = self._detect_platform()
            self.chip_count = self._guess_chip_count()
    
    def _detect_platform(self) -> str:
        if self.vendor_id == "8086":
            return "Intel Platform"
        if self.vendor_id == "1022":
            return "AMD Platform"
        if self.vendor_id in ("1B21", "1B73", "1106", "104C"):
            return "Third-Party Controller"
        return "Unknown Platform"
    
    def _guess_chip_count(self) -> int:
        name_lower = self.name.lower()
        if "thunderbolt" in name_lower or "hub" in name_lower:
            return 2
        if self.vendor_id in ("1B21", "1B73", "1106", "104C"):
            return 1
        if "chipset" in name_lower:
            return 1
        return 0
    
    @property
    def display_name(self) -> str:
        return self.db_name
    
    @property
    def vid_did_str(self) -> str:
        return f"VID:{self.vendor_id} DID:{self.device_id}"
    
    @property
    def irq_status(self) -> str:
        if self.msi_enabled:
            return "MSI (low latency interrupts)"
        return "Line-based (higher latency)"
    
    @property
    def chip_location(self) -> str:
        if self.chip_count == 0:
            return "INSIDE CPU"
        if self.chip_count == 1:
            return "CHIPSET"
        return "EXTERNAL/HUB"


class UsbDeviceInfo:
    def __init__(self, data: dict):
        self.name = data.get("Name", "Unknown Device")
        self.device_class = data.get("Class", "")
        self.instance_id = data.get("InstanceId", "")
        self.vendor_id = str(data.get("VendorId", "")).upper()
        self.product_id = str(data.get("ProductId", "")).upper()
        self.controller: Optional[UsbControllerInfo] = None
        self.root_hub_id = self._extract_root_hub_id()
    
    def _extract_root_hub_id(self) -> str:
        iid = self.instance_id.upper()
        if "USB\\" in iid:
            parts = iid.split("\\")
            for i, part in enumerate(parts):
                if part.startswith("VID_"):
                    return "\\".join(parts[:i+1]) if i > 0 else ""
        return ""
    
    def is_interesting(self) -> bool:
        return self.device_class.lower() in ("mouse", "keyboard", "media", "audioendpoint")
    
    @property
    def vid_pid_str(self) -> str:
        if self.vendor_id and self.product_id:
            return f"VID:{self.vendor_id} PID:{self.product_id}"
        return ""
    
    def get_path_style(self) -> PathStyle:
        if self.controller:
            chip_count = self.controller.chip_count
        else:
            return PathStyle(TEXT_MUTED, "Unknown", "[--?--]", "#12121a")
        
        if chip_count == 0:
            return PathStyle(ACCENT_EMERALD, "Direct Path", "[---->]", "#0d1f15")
        if chip_count == 1:
            return PathStyle(ACCENT_CYAN, "Via Chipset", "[-->o->]", "#0d1a1f")
        return PathStyle(TEXT_WARNING, "Extended Path", "[->o->o->]", "#1f1a0d")
    
    def get_device_icon(self) -> str:
        device_class = self.device_class.lower()
        name_lower = self.name.lower()
        
        if "mouse" in device_class or "mouse" in name_lower or any(x in name_lower for x in ("razer", "deathadder", "logitech g")):
            return "[M]"
        if "keyboard" in device_class or "keyboard" in name_lower:
            return "[K]"
        if "audio" in device_class or "audio" in name_lower or "media" in device_class:
            return "[A]"
        return "[D]"


class UsbDeviceMapper:
    def __init__(self, controllers: List[UsbControllerInfo], devices: List[UsbDeviceInfo]):
        self._controllers = controllers
        self._devices = devices
    
    def map_devices_to_controllers(self) -> None:
        vid_pid_to_controller = self._build_controller_map()
        
        interesting_devices = [d for d in self._devices if d.is_interesting()]
        
        for dev in interesting_devices:
            vid_pid = f"{dev.vendor_id}:{dev.product_id}"
            
            if vid_pid in vid_pid_to_controller:
                ctrl = vid_pid_to_controller[vid_pid]
                ctrl.devices.append(dev)
                dev.controller = ctrl
                continue
            
            self._assign_fallback_controller(dev)
    
    def _build_controller_map(self) -> Dict[str, UsbControllerInfo]:
        import wmi
        c = wmi.WMI()
        vid_pid_to_controller = {}
        
        try:
            for entity in c.Win32_USBControllerDevice():
                antecedent = str(entity.Antecedent)
                dependent = str(entity.Dependent)
                
                ctrl_match = re.search(r'DeviceID\s*=\s*"([^"]+)"', antecedent)
                dev_match = re.search(r'DeviceID\s*=\s*"([^"]+)"', dependent)
                
                if ctrl_match and dev_match:
                    ctrl_id = ctrl_match.group(1).replace("\\\\", "\\").upper()
                    dev_id = dev_match.group(1).replace("\\\\", "\\").upper()
                    
                    vid_match = re.search(r'VID_([0-9A-Fa-f]{4})', dev_id, re.I)
                    pid_match = re.search(r'PID_([0-9A-Fa-f]{4})', dev_id, re.I)
                    
                    if vid_match and pid_match:
                        vid_pid = f"{vid_match.group(1).upper()}:{pid_match.group(1).upper()}"
                        
                        for ctrl in self._controllers:
                            if ctrl.instance_id.upper() == ctrl_id:
                                vid_pid_to_controller[vid_pid] = ctrl
                                break
        except (AttributeError, RuntimeError):
            pass
        
        return vid_pid_to_controller
    
    def _assign_fallback_controller(self, dev: UsbDeviceInfo) -> None:
        if not self._controllers:
            return
        
        for ctrl in self._controllers:
            if ctrl.chip_count >= 1:
                ctrl.devices.append(dev)
                dev.controller = ctrl
                return
        
        ctrl = self._controllers[0]
        ctrl.devices.append(dev)
        dev.controller = ctrl


class UsbCardBuilder:
    def __init__(self, parent: ctk.CTkFrame):
        self._parent = parent
    
    def create_device_card(self, dev: UsbDeviceInfo) -> None:
        path_style = dev.get_path_style()
        controller_name = dev.controller.display_name if dev.controller else "Unknown Controller"
        msi_enabled = dev.controller.msi_enabled if dev.controller else False
        platform = dev.controller.platform_info if dev.controller else ""
        
        card = ctk.CTkFrame(
            self._parent,
            fg_color="#0f0f16",
            corner_radius=14,
            border_color="#1a1a24",
            border_width=1
        )
        card.pack(fill="x", padx=14, pady=6)
        
        accent_bar = ctk.CTkFrame(card, fg_color=path_style.color, width=4, corner_radius=2)
        accent_bar.pack(side="left", fill="y", padx=(0, 0), pady=0)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=14)
        
        self._build_top_section(content, dev, path_style)
        
        separator = ctk.CTkFrame(content, fg_color="#1a1a24", height=1)
        separator.pack(fill="x", pady=(12, 10))
        
        self._build_details_section(content, controller_name, platform, msi_enabled)
    
    def _build_top_section(self, content: ctk.CTkFrame, dev: UsbDeviceInfo, path_style: PathStyle) -> None:
        top_section = ctk.CTkFrame(content, fg_color="transparent")
        top_section.pack(fill="x")
        
        device_info = ctk.CTkFrame(top_section, fg_color="transparent")
        device_info.pack(side="left", fill="x", expand=True)
        
        name_row = ctk.CTkFrame(device_info, fg_color="transparent")
        name_row.pack(anchor="w")
        
        ctk.CTkLabel(
            name_row, text=dev.get_device_icon(),
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=path_style.color
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            name_row, text=dev.name,
            font=ctk.CTkFont(family="Segoe UI Semibold", size=13),
            text_color="#e0e0e8"
        ).pack(side="left")
        
        if dev.vid_pid_str:
            ctk.CTkLabel(
                device_info, text=dev.vid_pid_str,
                font=ctk.CTkFont(family="JetBrains Mono, Consolas", size=10),
                text_color="#505060"
            ).pack(anchor="w", pady=(3, 0))
        
        self._build_path_badge(top_section, path_style)
    
    def _build_path_badge(self, parent: ctk.CTkFrame, path_style: PathStyle) -> None:
        path_badge = ctk.CTkFrame(parent, fg_color=path_style.bg_tint, corner_radius=10)
        path_badge.pack(side="right")
        
        badge_inner = ctk.CTkFrame(path_badge, fg_color="transparent")
        badge_inner.pack(padx=12, pady=8)
        
        ctk.CTkLabel(
            badge_inner, text=path_style.visual,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=path_style.color
        ).pack()
        
        ctk.CTkLabel(
            badge_inner, text=path_style.label,
            font=ctk.CTkFont(family="Segoe UI Semibold", size=10),
            text_color=path_style.color
        ).pack(pady=(2, 0))
    
    def _build_details_section(self, content: ctk.CTkFrame, controller_name: str, platform: str, msi_enabled: bool) -> None:
        details_grid = ctk.CTkFrame(content, fg_color="transparent")
        details_grid.pack(fill="x")
        
        left_details = ctk.CTkFrame(details_grid, fg_color="transparent")
        left_details.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            left_details, text="CONTROLLER",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#404050"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            left_details, text=controller_name,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#909098"
        ).pack(anchor="w", pady=(2, 0))
        
        if platform:
            ctk.CTkLabel(
                left_details, text=platform,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#505060"
            ).pack(anchor="w", pady=(1, 0))
        
        right_details = ctk.CTkFrame(details_grid, fg_color="transparent")
        right_details.pack(side="right")
        
        irq_frame = ctk.CTkFrame(right_details, fg_color="transparent")
        irq_frame.pack(anchor="e")
        
        irq_color = ACCENT_EMERALD if msi_enabled else "#606070"
        irq_text = "MSI Enabled" if msi_enabled else "Legacy IRQ"
        irq_icon = "✓" if msi_enabled else "○"
        
        ctk.CTkLabel(
            irq_frame, text=irq_icon,
            font=ctk.CTkFont(size=11),
            text_color=irq_color
        ).pack(side="left", padx=(0, 4))
        
        ctk.CTkLabel(
            irq_frame, text=irq_text,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=irq_color
        ).pack(side="left")


class UsbLatencyDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("USB Chipset Mapper")
        self.geometry("720x680")
        self.configure(fg_color="#08080c")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        from utils.helpers import set_window_icon
        import pywinstyles
        set_window_icon(self)
        pywinstyles.change_header_color(self, "#08080c")
        
        self._is_destroyed = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._controllers: List[UsbControllerInfo] = []
        self._devices: List[UsbDeviceInfo] = []
        self._interesting_devices: List[UsbDeviceInfo] = []
        self._selective_suspend: Optional[Dict] = None
        
        self._build_ui()
        self._center_window(parent)
        self._load_data()
    
    def _on_close(self):
        self._is_destroyed = True
        self.destroy()
    
    def _center_window(self, parent):
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _build_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=28, pady=24)
        
        self._build_hero_header(main_container)
        self._build_pathway_legend(main_container)
        self._build_scroll_area(main_container)
        self._build_action_bar(main_container)
    
    def _build_hero_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        left_section = ctk.CTkFrame(header, fg_color="transparent")
        left_section.pack(side="left", fill="x", expand=True)
        
        title_row = ctk.CTkFrame(left_section, fg_color="transparent")
        title_row.pack(anchor="w")
        
        icon_frame = ctk.CTkFrame(title_row, fg_color="#1a1025", corner_radius=12, width=44, height=44)
        icon_frame.pack(side="left", padx=(0, 14))
        icon_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_frame, text="⚡",
            font=ctk.CTkFont(size=20),
            text_color=ACCENT_PURPLE
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        title_text = ctk.CTkFrame(title_row, fg_color="transparent")
        title_text.pack(side="left")
        
        ctk.CTkLabel(
            title_text, text="Chipset Mapper",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_text, text="USB Signal Path Analysis",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#6b6b80"
        ).pack(anchor="w", pady=(2, 0))
        
        self._status_indicator = ctk.CTkFrame(header, fg_color="#12121a", corner_radius=16, height=32)
        self._status_indicator.pack(side="right", pady=(8, 0))
        
        self._status_dot = ctk.CTkFrame(self._status_indicator, fg_color=TEXT_MUTED, width=8, height=8, corner_radius=4)
        self._status_dot.pack(side="left", padx=(12, 6), pady=12)
        
        self._status_text = ctk.CTkLabel(
            self._status_indicator, text="Initializing",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED
        )
        self._status_text.pack(side="left", padx=(0, 14), pady=6)
    
    def _build_pathway_legend(self, parent):
        legend_container = ctk.CTkFrame(parent, fg_color="#0e0e14", corner_radius=14)
        legend_container.pack(fill="x", pady=(0, 16))
        
        inner = ctk.CTkFrame(legend_container, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)
        
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")
        
        ctk.CTkLabel(
            top_row, text="Signal Path Rating",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color="#9090a0"
        ).pack(side="left")
        
        divider = ctk.CTkFrame(inner, fg_color="#1a1a24", height=1)
        divider.pack(fill="x", pady=(12, 14))
        
        pathways_frame = ctk.CTkFrame(inner, fg_color="transparent")
        pathways_frame.pack(fill="x")
        
        pathways = [
            (ACCENT_EMERALD, "Direct", "0 hops", "CPU integrated", "[---->]"),
            (ACCENT_CYAN, "Optimal", "1 hop", "Via chipset", "[-->o->]"),
            (TEXT_WARNING, "Extended", "2+ hops", "Via hub/bridge", "[->o->o->]"),
        ]
        
        for i, (color, label, hops, desc, visual) in enumerate(pathways):
            path_card = ctk.CTkFrame(pathways_frame, fg_color="transparent")
            path_card.pack(side="left", expand=True, fill="x", padx=(0 if i == 0 else 8, 0))
            
            indicator_bar = ctk.CTkFrame(path_card, fg_color=color, height=3, corner_radius=2)
            indicator_bar.pack(fill="x", pady=(0, 8))
            
            ctk.CTkLabel(
                path_card, text=visual,
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=color
            ).pack(anchor="w")
            
            info_row = ctk.CTkFrame(path_card, fg_color="transparent")
            info_row.pack(fill="x", pady=(4, 0))
            
            ctk.CTkLabel(
                info_row, text=label,
                font=ctk.CTkFont(family="Segoe UI Semibold", size=11),
                text_color=color
            ).pack(side="left")
            
            ctk.CTkLabel(
                info_row, text=hops,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#606070"
            ).pack(side="right")
            
            ctk.CTkLabel(
                path_card, text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#505060"
            ).pack(anchor="w", pady=(2, 0))
    
    def _build_scroll_area(self, parent):
        scroll_container = ctk.CTkFrame(parent, fg_color="#0a0a0f", corner_radius=12)
        scroll_container.pack(fill="both", expand=True, pady=(0, 16))
        
        self._scroll_frame = ctk.CTkScrollableFrame(
            scroll_container,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#1e1e2a",
            scrollbar_button_hover_color=ACCENT_PURPLE
        )
        self._scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)
    
    def _build_action_bar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x")
        
        refresh_btn = ctk.CTkButton(
            bar, text="⟳  Rescan",
            command=self._load_data,
            fg_color="#1a1025",
            hover_color="#251535",
            text_color=ACCENT_PURPLE,
            border_color="#2a1a3a",
            border_width=1,
            corner_radius=10,
            height=38,
            width=110,
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12)
        )
        refresh_btn.pack(side="left")
        
        close_btn = ctk.CTkButton(
            bar, text="Done",
            command=self._on_close,
            fg_color=ACCENT_PURPLE,
            hover_color="#9045e7",
            text_color="#ffffff",
            corner_radius=10,
            height=38,
            width=90,
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12)
        )
        close_btn.pack(side="right")
    
    def _show_loading(self):
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        
        loading_frame = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        loading_frame.pack(expand=True, pady=60)
        
        ctk.CTkLabel(
            loading_frame, text="◌",
            font=ctk.CTkFont(size=32),
            text_color=ACCENT_PURPLE
        ).pack()
        
        ctk.CTkLabel(
            loading_frame, text="Scanning USB topology...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#606070"
        ).pack(pady=(12, 0))
        
        self._status_dot.configure(fg_color=TEXT_WARNING)
        self._status_text.configure(text="Scanning", text_color=TEXT_WARNING)
    
    def _load_data(self):
        self._show_loading()
        threading.Thread(target=self._fetch_data, daemon=True).start()
    
    def _fetch_data(self):
        pythoncom.CoInitialize()
        try:
            controllers_raw = UsbDataFetcher.get_controllers()
            self._controllers = [UsbControllerInfo(c) for c in controllers_raw]
            
            devices_raw = UsbDataFetcher.get_devices()
            self._devices = [UsbDeviceInfo(d) for d in devices_raw]
            
            self._interesting_devices = [d for d in self._devices if d.is_interesting()]
            
            mapper = UsbDeviceMapper(self._controllers, self._devices)
            mapper.map_devices_to_controllers()
            
            self._selective_suspend = UsbDataFetcher.get_selective_suspend()
            
            self.after(0, self._display_results)
        except (RuntimeError, AttributeError, ImportError) as e:
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: self._display_error(msg))
        finally:
            pythoncom.CoUninitialize()
    
    def _display_results(self):
        if self._is_destroyed:
            return
        
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        
        self._status_dot.configure(fg_color=ACCENT_EMERALD)
        self._status_text.configure(text="Ready", text_color=ACCENT_EMERALD)
        
        if not self._interesting_devices:
            self._display_empty_state()
            return
        
        devices_header = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        devices_header.pack(fill="x", padx=16, pady=(16, 12))
        
        ctk.CTkLabel(
            devices_header, text="Detected Devices",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=13),
            text_color="#9090a0"
        ).pack(side="left")
        
        count_badge = ctk.CTkFrame(devices_header, fg_color="#1a1a24", corner_radius=10)
        count_badge.pack(side="right")
        
        ctk.CTkLabel(
            count_badge, text=str(len(self._interesting_devices)),
            font=ctk.CTkFont(family="Segoe UI Semibold", size=11),
            text_color=ACCENT_PURPLE
        ).pack(padx=10, pady=4)
        
        card_builder = UsbCardBuilder(self._scroll_frame)
        for dev in self._interesting_devices:
            card_builder.create_device_card(dev)
    
    def _display_empty_state(self):
        empty = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        empty.pack(expand=True, pady=60)
        
        ctk.CTkLabel(
            empty, text="∅",
            font=ctk.CTkFont(size=40),
            text_color="#303040"
        ).pack()
        
        ctk.CTkLabel(
            empty, text="No input devices found",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#505060"
        ).pack(pady=(12, 4))
        
        ctk.CTkLabel(
            empty, text="Connect a mouse or keyboard to analyze",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#404050"
        ).pack()
    
    def _display_error(self, error: str):
        if self._is_destroyed:
            return
        
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        
        self._status_dot.configure(fg_color=TEXT_ERROR)
        self._status_text.configure(text="Error", text_color=TEXT_ERROR)
        
        error_frame = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        error_frame.pack(expand=True, pady=60)
        
        ctk.CTkLabel(
            error_frame, text="⚠",
            font=ctk.CTkFont(size=32),
            text_color=TEXT_ERROR
        ).pack()
        
        ctk.CTkLabel(
            error_frame, text="Analysis Failed",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=13),
            text_color=TEXT_ERROR
        ).pack(pady=(12, 4))
        
        ctk.CTkLabel(
            error_frame, text=error[:100],
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#505060"
        ).pack()


def show_usb_latency_dialog(parent) -> None:
    dialog = UsbLatencyDialog(parent)
    dialog.wait_window()