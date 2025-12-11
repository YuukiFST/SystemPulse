import customtkinter as ctk
import sys
import os
import pywinstyles
from tkinter import messagebox

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


class AnimatedButton(ctk.CTkButton):
    def __init__(self, master, text: str, command, **kwargs):
        self._base_color = BG_CARD
        self._hover_color = BG_ELEVATED
        self.glow_color = ACCENT_CYAN
        self._text_normal = TEXT_PRIMARY
        self.text_hover = ACCENT_CYAN
        self._user_command = command
        
        super().__init__(
            master,
            text=text,
            command=self._on_click,
            fg_color=self._base_color,
            hover_color=self._hover_color,
            text_color=self._text_normal,
            border_color=BORDER_SUBTLE,
            border_width=1,
            corner_radius=12,
            height=52,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            anchor="center",
            **kwargs
        )
        
        self._animation_running = False
        self._clicked = False
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_click(self) -> None:
        self._clicked = True
        self._animation_running = False
        self._reset_style()
        if self._user_command:
            self._user_command()
        self.after(100, self._finish_click)
    
    def _finish_click(self) -> None:
        self._clicked = False
    
    def _reset_style(self) -> None:
        try:
            self.configure(
                border_color=BORDER_SUBTLE,
                text_color=self._text_normal,
                border_width=1
            )
        except (AttributeError, RuntimeError):
            pass
    
    def _on_enter(self, event=None) -> None:
        if self._clicked:
            return
        self._animation_running = True
        self._animate_hover_in(0)
    
    def _on_leave(self, event=None) -> None:
        if self._clicked:
            return
        self._animation_running = False
        self._animate_hover_out(0)
    
    def _animate_hover_in(self, step: int) -> None:
        if not self._animation_running or step > ANIMATION_HOVER_STEPS or self._clicked:
            return
        
        progress = step / ANIMATION_HOVER_STEPS
        try:
            self.configure(
                border_color=interpolate_color(BORDER_SUBTLE, self.glow_color, progress),
                text_color=interpolate_color(self._text_normal, self.text_hover, progress),
                border_width=1 + int(progress * 1)
            )
        except (AttributeError, RuntimeError):
            return
        
        self.after(ANIMATION_STEP_DURATION_MS, lambda: self._animate_hover_in(step + 1))
    
    def _animate_hover_out(self, step: int) -> None:
        if self._animation_running or step > ANIMATION_HOVER_STEPS or self._clicked:
            return
        
        progress = step / ANIMATION_HOVER_STEPS
        try:
            self.configure(
                border_color=interpolate_color(self.glow_color, BORDER_SUBTLE, progress),
                text_color=interpolate_color(self.text_hover, self._text_normal, progress),
                border_width=2 - int(progress * 1)
            )
        except (AttributeError, RuntimeError):
            return
        
        self.after(ANIMATION_STEP_DURATION_MS, lambda: self._animate_hover_out(step + 1))


class FluxCheckApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._root = ctk.CTk()
        self._root.title("SystemPulse")
        self._root.geometry("460x640")
        self._root.resizable(False, False)
        self._root.configure(fg_color=BG_VOID)
        
        pywinstyles.change_header_color(self._root, "#050508")
        set_window_icon(self._root)
        
        self._title_label = None
        self._glow_frame = None
        self._animation_step = 0
        self._glow_colors = [ACCENT_CYAN, ACCENT_PURPLE, ACCENT_PINK, ACCENT_EMERALD]
        
        self._build_ui()
        self._animate_title_glow()
        
    def _build_ui(self) -> None:
        self._build_header()
        self._build_divider()
        self._build_buttons()
    
    def _build_header(self) -> None:
        header_frame = ctk.CTkFrame(self._root, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(40, 10))
        
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack()
        
        self._glow_frame = ctk.CTkFrame(
            title_container, 
            fg_color="transparent",
            corner_radius=20
        )
        self._glow_frame.pack()
        
        self._title_label = ctk.CTkLabel(
            self._glow_frame, 
            text="SystemPulse", 
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=ACCENT_CYAN
        )
        self._title_label.pack(padx=10, pady=5)
        
        ctk.CTkLabel(
            header_frame, 
            text="System Diagnostics & Optimization", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_SECONDARY
        ).pack(pady=(5, 0))
    
    def _animate_title_glow(self) -> None:
        if not self._title_label or not self._title_label.winfo_exists():
            return
        
        color_idx = self._animation_step // ANIMATION_TITLE_CYCLE_FRAMES
        sub_step = self._animation_step % ANIMATION_TITLE_CYCLE_FRAMES
        
        current_color = self._glow_colors[color_idx % len(self._glow_colors)]
        next_color = self._glow_colors[(color_idx + 1) % len(self._glow_colors)]
        
        progress = sub_step / float(ANIMATION_TITLE_CYCLE_FRAMES)
        blended = interpolate_color(current_color, next_color, progress)
        
        try:
            self._title_label.configure(text_color=blended)
        except (AttributeError, RuntimeError):
            pass
        
        self._animation_step = (self._animation_step + 1) % (ANIMATION_TITLE_CYCLE_FRAMES * len(self._glow_colors))
        self._root.after(ANIMATION_TITLE_STEP_DURATION_MS, self._animate_title_glow)
    
    def _build_divider(self) -> None:
        ctk.CTkFrame(self._root, fg_color=BORDER_GLOW, height=1).pack(
            fill="x", padx=50, pady=(25, 30)
        )
    
    def _build_buttons(self) -> None:
        btn_frame = ctk.CTkFrame(self._root, fg_color="transparent")
        btn_frame.pack(fill="both", expand=True, padx=40)
        
        buttons = [
            ("CPU Core Inspector", self._run_physical_cores, ACCENT_CYAN),
            ("Disk Health Scan", self._run_disk_corruption, ACCENT_EMERALD),
            ("USB Chipset Mapper", self._run_usb_latency, ACCENT_PURPLE),
            ("Network Latency Tester", self._run_input_lag, ACCENT_PINK),
            ("Driver Registry Viewer", self._run_driver_registry, ACCENT_PINK),
            ("Dependency Map", self._run_service_dependency, ACCENT_CYAN)
        ]
        
        for text, cmd, accent in buttons:
            btn = AnimatedButton(btn_frame, text=text, command=cmd)
            btn.glow_color = accent
            btn.text_hover = accent
            btn.pack(fill="x", pady=8)
               
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
