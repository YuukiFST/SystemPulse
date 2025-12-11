import customtkinter as ctk
import sys
import os
import pywinstyles
from tkinter import messagebox
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.driver_registry_dialog import show_driver_registry_keys_dialog
from gui.service_dependency_dialog import show_service_dependency_dialog
from gui.physical_cores_dialog import show_physical_cores_dialog
from gui.disk_corruption_dialog import show_disk_corruption_dialog
from gui.usb_latency_dialog import show_usb_latency_dialog
from gui.input_lag_dialog import show_input_lag_dialog
from gui.theme import (
    BG_VOID, BG_CARD, BG_ELEVATED, BORDER_SUBTLE, BORDER_GLOW,
    ACCENT_CYAN, ACCENT_PURPLE, ACCENT_PINK, ACCENT_EMERALD,
    TEXT_PRIMARY, TEXT_SECONDARY, interpolate_color
)
from utils.helpers import set_window_icon
from utils.constants import (
    ANIMATION_STEP_DURATION_MS, ANIMATION_HOVER_STEPS,
    ANIMATION_TITLE_STEP_DURATION_MS, ANIMATION_TITLE_CYCLE_FRAMES
)


class TechCard(ctk.CTkFrame):
    def __init__(self, master, text: str, subtitle: str, command, accent: str, icon: str, delay: int = 0, **kwargs):
        super().__init__(
            master,
            fg_color="#08080c",
            corner_radius=12,
            border_color="#15151f",
            border_width=1,
            **kwargs
        )
        
        self._command = command
        self._accent = accent
        self._is_hovered = False
        self._glow_phase = 0
        
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=20, pady=16)
        
        header = ctk.CTkFrame(self._content, fg_color="transparent")
        header.pack(fill="x")
        
        left_section = ctk.CTkFrame(header, fg_color="transparent")
        left_section.pack(side="left", fill="x", expand=True)
        
        self._icon_frame = ctk.CTkFrame(
            left_section,
            width=36,
            height=36,
            corner_radius=8,
            fg_color="#0c0c12",
            border_width=1,
            border_color="#1a1a26"
        )
        self._icon_frame.pack(side="left")
        self._icon_frame.pack_propagate(False)
        
        self._icon_label = ctk.CTkLabel(
            self._icon_frame,
            text=icon,
            font=ctk.CTkFont(size=16),
            text_color="#404055"
        )
        self._icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        text_section = ctk.CTkFrame(left_section, fg_color="transparent")
        text_section.pack(side="left", padx=(14, 0), fill="x", expand=True)
        
        self._title = ctk.CTkLabel(
            text_section,
            text=text,
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color="#c8c8d8",
            anchor="w"
        )
        self._title.pack(fill="x")
        
        self._subtitle = ctk.CTkLabel(
            text_section,
            text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#4a4a5c",
            anchor="w"
        )
        self._subtitle.pack(fill="x", pady=(2, 0))
        
        self._chevron = ctk.CTkLabel(
            header,
            text="›",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#25252f"
        )
        self._chevron.pack(side="right", padx=(10, 0))
        
        self._indicator = ctk.CTkFrame(
            self,
            width=3,
            height=0,
            corner_radius=2,
            fg_color=accent
        )
        self._indicator.place(x=0, rely=0.5, anchor="w")
        
        for w in [self, self._content, header, left_section, self._icon_frame, 
                  self._icon_label, text_section, self._title, self._subtitle, self._chevron]:
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click)
        
        self._target_height = 32
        self._current_height = 0
        self.after(delay, self._slide_in)
    
    def _slide_in(self):
        if self._current_height < self._target_height:
            self._current_height += 4
            self._indicator.configure(height=min(self._current_height, self._target_height))
            self.after(20, self._slide_in)
    
    def _on_enter(self, event=None):
        if self._is_hovered:
            return
        self._is_hovered = True
        
        self.configure(fg_color="#0a0a10", border_color="#1e1e2c")
        self._icon_frame.configure(fg_color=self._accent, border_color=self._accent)
        self._icon_label.configure(text_color="#000000")
        self._title.configure(text_color="#ffffff")
        self._subtitle.configure(text_color="#6a6a80")
        self._chevron.configure(text_color=self._accent)
        self._indicator.configure(height=40)
    
    def _on_leave(self, event=None):
        if not self._is_hovered:
            return
        
        if event:
            x, y = self.winfo_pointerxy()
            w = self.winfo_containing(x, y)
            if w and (w == self or str(w).startswith(str(self))):
                return
        
        self._is_hovered = False
        
        self.configure(fg_color="#08080c", border_color="#15151f")
        self._icon_frame.configure(fg_color="#0c0c12", border_color="#1a1a26")
        self._icon_label.configure(text_color="#404055")
        self._title.configure(text_color="#c8c8d8")
        self._subtitle.configure(text_color="#4a4a5c")
        self._chevron.configure(text_color="#25252f")
        self._indicator.configure(height=32)
    
    def _on_click(self, event=None):
        if self._command:
            self.configure(fg_color="#050508")
            self.after(80, lambda: self.configure(fg_color="#0a0a10" if self._is_hovered else "#08080c"))
            self._command()


class FluxCheckApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._root = ctk.CTk()
        self._root.title("SystemPulse")
        self._root.geometry("480x780")
        self._root.resizable(False, False)
        self._root.configure(fg_color="#030305")
        
        pywinstyles.change_header_color(self._root, "#030305")
        set_window_icon(self._root)
        
        self._title_label = None
        self._animation_step = 0
        
        self._build_ui()
        self._animate_title()
        
    def _build_ui(self) -> None:
        self._build_header()
        self._build_cards()
        self._build_footer()
    
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self._root, fg_color="transparent")
        header.pack(fill="x", padx=36, pady=(40, 20))
        
        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.pack()
        
        self._title_label = ctk.CTkLabel(
            brand, 
            text="SYSTEMPULSE",
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color="#00d4ff"
        )
        self._title_label.pack()
        
        sub = ctk.CTkLabel(
            header,
            text="DIAGNOSTIC SUITE",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color="#2a2a38"
        )
        sub.pack(pady=(6, 0))
        
        divider = ctk.CTkFrame(header, height=1, fg_color="#12121a")
        divider.pack(fill="x", pady=(20, 0))
    
    def _animate_title(self) -> None:
        if not self._title_label or not self._title_label.winfo_exists():
            return
        
        phase = (self._animation_step % 60) / 60
        r = int(0 + 20 * math.sin(phase * math.pi * 2))
        g = int(200 + 20 * math.sin(phase * math.pi * 2))
        b = int(255)
        color = f"#{max(0,r):02x}{g:02x}{b:02x}"
        
        try:
            self._title_label.configure(text_color=color)
        except:
            pass
        
        self._animation_step += 1
        self._root.after(100, self._animate_title)
    
    def _build_cards(self) -> None:
        container = ctk.CTkFrame(self._root, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=36, pady=16)
        
        cards = [
            ("CPU Inspector", "Physical cores & topology", self._run_physical_cores, "#00d4ff", "◎"),
            ("Disk Scanner", "Filesystem integrity check", self._run_disk_corruption, "#10b981", "◈"),
            ("USB Mapper", "Controller & port mapping", self._run_usb_latency, "#a855f7", "◇"),
            ("Network Probe", "Connection latency test", self._run_input_lag, "#f472b6", "◆"),
            ("Driver Registry", "Configuration viewer", self._run_driver_registry, "#fb923c", "▣"),
            ("Service Map", "Dependency analysis", self._run_service_dependency, "#06b6d4", "◉"),
        ]
        
        for i, (title, sub, cmd, accent, icon) in enumerate(cards):
            card = TechCard(
                container,
                text=title,
                subtitle=sub,
                command=cmd,
                accent=accent,
                icon=icon,
                delay=i * 50
            )
            card.pack(fill="x", pady=5)
    
    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self._root, fg_color="transparent")
        footer.pack(fill="x", padx=36, pady=(0, 28))
        
        line = ctk.CTkFrame(footer, height=1, fg_color="#12121a")
        line.pack(fill="x", pady=(0, 14))
        
        ver = ctk.CTkLabel(
            footer,
            text="v1.0.0",
            font=ctk.CTkFont(family="Consolas", size=9),
            text_color="#1a1a24"
        )
        ver.pack()
       
    def _run_physical_cores(self) -> None:
        show_physical_cores_dialog(self._root)
        
    def _run_disk_corruption(self) -> None:
        proceed = messagebox.askyesno(
            "Warning",
            "Once the Disk Corruption Checker starts, you must wait for it to finish.\n\n"
            "Do not close the window until all operations are complete.\n\n"
            "Do you want to continue?"
        )
        if proceed:
            show_disk_corruption_dialog(self._root)
    
    def _run_usb_latency(self) -> None:
        show_usb_latency_dialog(self._root)
        
    def _run_input_lag(self) -> None:
        show_input_lag_dialog(self._root)
        
    def _run_driver_registry(self) -> None:
        show_driver_registry_keys_dialog(self._root)
        
    def _run_service_dependency(self) -> None:
        show_service_dependency_dialog(self._root)
        
    def run(self) -> None:
        self._root.mainloop()


if __name__ == "__main__":
    app = FluxCheckApp()
    app.run()