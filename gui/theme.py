import customtkinter as ctk
from dataclasses import dataclass
from typing import Callable, Optional
from utils.constants import ANIMATION_STEP_DURATION_MS, ANIMATION_GLOW_STEPS


@dataclass(frozen=True)
class Colors:
    BG_VOID = "#050508"
    BG_SURFACE = "#0c0c10"
    BG_CARD = "#12121a"
    BG_ELEVATED = "#1a1a24"
    BG_HOVER = "#22222e"
    BORDER_SUBTLE = "#1e1e2a"
    BORDER_GLOW = "#2d2d40"
    ACCENT_CYAN = "#00d4ff"
    ACCENT_CYAN_DIM = "#00a8cc"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_PINK = "#ec4899"
    ACCENT_EMERALD = "#10b981"
    TEXT_PRIMARY = "#f0f0f5"
    TEXT_SECONDARY = "#8888a0"
    TEXT_MUTED = "#555566"
    TEXT_SUCCESS = "#22c55e"
    TEXT_WARNING = "#f59e0b"
    TEXT_ERROR = "#ef4444"


COLORS = Colors()

BG_VOID = COLORS.BG_VOID
BG_SURFACE = COLORS.BG_SURFACE
BG_CARD = COLORS.BG_CARD
BG_ELEVATED = COLORS.BG_ELEVATED
BG_HOVER = COLORS.BG_HOVER
BORDER_SUBTLE = COLORS.BORDER_SUBTLE
BORDER_GLOW = COLORS.BORDER_GLOW
ACCENT_CYAN = COLORS.ACCENT_CYAN
ACCENT_CYAN_DIM = COLORS.ACCENT_CYAN_DIM
ACCENT_PURPLE = COLORS.ACCENT_PURPLE
ACCENT_PINK = COLORS.ACCENT_PINK
ACCENT_EMERALD = COLORS.ACCENT_EMERALD
TEXT_PRIMARY = COLORS.TEXT_PRIMARY
TEXT_SECONDARY = COLORS.TEXT_SECONDARY
TEXT_MUTED = COLORS.TEXT_MUTED
TEXT_SUCCESS = COLORS.TEXT_SUCCESS
TEXT_WARNING = COLORS.TEXT_WARNING
TEXT_ERROR = COLORS.TEXT_ERROR


def interpolate_color(color1: str, color2: str, t: float) -> str:
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"


def darken_color(color: str, factor: float) -> str:
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return f"#{int(r*(1-factor)):02x}{int(g*(1-factor)):02x}{int(b*(1-factor)):02x}"


class GlowButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        text: str,
        command: Optional[Callable] = None,
        accent: str = ACCENT_CYAN,
        icon: str = "",
        width: int = 80,
        height: int = 32,
        **kwargs
    ):
        self.accent = accent
        self._base_fg = BG_CARD
        self._hover_fg = BG_ELEVATED
        self._user_command = command
        
        super().__init__(
            master,
            text=f"{icon}  {text}" if icon else text,
            command=self._handle_click,
            fg_color=self._base_fg,
            hover_color=self._hover_fg,
            text_color=TEXT_PRIMARY,
            border_color=BORDER_SUBTLE,
            border_width=1,
            corner_radius=8,
            height=height,
            width=width,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            **kwargs
        )
        
        self._animation_active = False
        self._clicked = False
        self.bind("<Enter>", self._hover_in)
        self.bind("<Leave>", self._hover_out)
    
    def _handle_click(self) -> None:
        self._clicked = True
        self._animation_active = False
        self._reset_style()
        if self._user_command:
            self._user_command()
        self._clicked = False
    
    def _reset_style(self) -> None:
        try:
            self.configure(
                border_color=BORDER_SUBTLE,
                text_color=TEXT_PRIMARY,
                border_width=1
            )
        except (AttributeError, RuntimeError):
            pass
    
    def _hover_in(self, event) -> None:
        if self._clicked:
            return
        self._animation_active = True
        self._animate_in(0)
    
    def _hover_out(self, event) -> None:
        if self._clicked:
            return
        self._animation_active = False
        self._animate_out(0)
    
    def _animate_in(self, step: int) -> None:
        if not self._animation_active or step > ANIMATION_GLOW_STEPS or self._clicked:
            return
        t = step / ANIMATION_GLOW_STEPS
        try:
            self.configure(
                border_color=interpolate_color(BORDER_SUBTLE, self.accent, t),
                text_color=interpolate_color(TEXT_PRIMARY, self.accent, t),
                border_width=1 + int(t)
            )
        except (AttributeError, RuntimeError):
            return
        self.after(ANIMATION_STEP_DURATION_MS, lambda: self._animate_in(step + 1))
    
    def _animate_out(self, step: int) -> None:
        if self._animation_active or step > ANIMATION_GLOW_STEPS or self._clicked:
            return
        t = step / ANIMATION_GLOW_STEPS
        try:
            self.configure(
                border_color=interpolate_color(self.accent, BORDER_SUBTLE, t),
                text_color=interpolate_color(self.accent, TEXT_PRIMARY, t),
                border_width=2 - int(t)
            )
        except (AttributeError, RuntimeError):
            return
        self.after(ANIMATION_STEP_DURATION_MS, lambda: self._animate_out(step + 1))


class AccentButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        text: str,
        command: Optional[Callable] = None,
        accent: str = ACCENT_CYAN,
        **kwargs
    ):
        self.accent = accent
        self._accent_hover = darken_color(accent, 0.2)
        
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=accent,
            hover_color=self._accent_hover,
            text_color="#ffffff",
            corner_radius=8,
            height=32,
            width=90,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            **kwargs
        )


def create_card(parent, **kwargs) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=BG_CARD,
        corner_radius=12,
        border_color=BORDER_SUBTLE,
        border_width=1,
        **kwargs
    )


def create_scrollable(parent, **kwargs) -> ctk.CTkScrollableFrame:
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=BG_SURFACE,
        corner_radius=10,
        scrollbar_button_color=BORDER_GLOW,
        scrollbar_button_hover_color=ACCENT_CYAN_DIM,
        **kwargs
    )


def create_header(parent, text: str, subtitle: Optional[str] = None) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(
        frame,
        text=text,
        font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        text_color=TEXT_PRIMARY
    ).pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(
            frame,
            text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_SECONDARY
        ).pack(anchor="w")
    return frame


def create_section_label(parent, text: str) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text.upper(),
        font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
        text_color=TEXT_MUTED
    )


def create_info_row(parent, label: str, value: str, value_color: str = TEXT_PRIMARY) -> ctk.CTkFrame:
    row = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(
        row,
        text=label,
        font=ctk.CTkFont(family="Segoe UI", size=12),
        text_color=TEXT_SECONDARY
    ).pack(side="left")
    ctk.CTkLabel(
        row,
        text=value,
        font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        text_color=value_color
    ).pack(side="right")
    return row
