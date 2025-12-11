import customtkinter as ctk
from gui.theme import (
    BG_CARD, BG_ELEVATED, BORDER_SUBTLE, BORDER_GLOW, TEXT_PRIMARY
)


class ModernStyle:
    @staticmethod
    def apply() -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    @staticmethod
    def get_button_colors() -> dict:
        return {
            "fg_color": BG_ELEVATED,
            "hover_color": BORDER_SUBTLE,
            "border_color": BORDER_SUBTLE,
            "text_color": TEXT_PRIMARY
        }
    
    @staticmethod
    def get_frame_colors() -> dict:
        return {
            "fg_color": BG_CARD,
            "border_color": BORDER_SUBTLE
        }
    
    @staticmethod
    def get_scrollable_colors() -> dict:
        return {
            "fg_color": BG_CARD,
            "border_color": BORDER_SUBTLE,
            "scrollbar_button_color": BORDER_SUBTLE,
            "scrollbar_button_hover_color": BORDER_GLOW
        }
