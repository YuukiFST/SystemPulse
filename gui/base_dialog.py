import customtkinter as ctk
import pywinstyles
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from utils.helpers import set_window_icon
from gui.theme import (
    BG_VOID, BG_SURFACE, BG_CARD, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, AccentButton, create_scrollable
)


class BaseDialog(ctk.CTkToplevel, ABC):
    def __init__(
        self,
        parent,
        title: str,
        geometry: str = "600x450",
        resizable: Tuple[bool, bool] = (True, True)
    ):
        super().__init__(parent)
        self.title(title)
        self.configure(fg_color=BG_VOID)
        self.geometry(geometry)
        self.resizable(*resizable)
        set_window_icon(self)
        self.transient(parent)
        self.grab_set()
        
        self._is_destroyed = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._build_ui()
        self._center_window(parent)
        self.update_idletasks()
        pywinstyles.change_header_color(self, "#050508")
    
    def _on_close(self) -> None:
        if self._can_close():
            self._is_destroyed = True
            self.destroy()
    
    def _can_close(self) -> bool:
        return True
    
    def _center_window(self, parent) -> None:
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    @abstractmethod
    def _build_ui(self) -> None:
        pass
    
    def _safe_update(self, callback) -> None:
        def _update():
            if self._is_destroyed:
                return
            try:
                callback()
            except (RuntimeError, AttributeError):
                pass
        self.after(0, _update)


class ScrollableDialog(BaseDialog, ABC):
    def __init__(
        self,
        parent,
        title: str,
        header_text: str,
        geometry: str = "600x450",
        resizable: Tuple[bool, bool] = (True, True),
        accent_color: str = None
    ):
        self._header_text = header_text
        self._accent_color = accent_color
        super().__init__(parent, title, geometry, resizable)
    
    def _build_ui(self) -> None:
        self._build_header()
        self._build_content_area()
        self._build_footer()
        self._show_loading()
    
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 15))
        
        ctk.CTkLabel(
            header,
            text=self._header_text,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")
        
        self._build_header_extra(header)
    
    def _build_header_extra(self, header: ctk.CTkFrame) -> None:
        pass
    
    def _build_content_area(self) -> None:
        self.scroll_frame = create_scrollable(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
    
    def _build_footer(self) -> None:
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self._build_footer_left(btn_frame)
        self._build_footer_right(btn_frame)
    
    def _build_footer_left(self, footer: ctk.CTkFrame) -> None:
        pass
    
    def _build_footer_right(self, footer: ctk.CTkFrame) -> None:
        accent = self._accent_color or TEXT_PRIMARY
        AccentButton(footer, text="Close", command=self.destroy, accent=accent).pack(side="right")
    
    def _show_loading(self, message: str = "Loading...") -> None:
        self.loading_label = ctk.CTkLabel(
            self.scroll_frame,
            text=f"⏳ {message}",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED
        )
        self.loading_label.pack(pady=40)
    
    def _clear_scroll_frame(self) -> None:
        try:
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
        except (RuntimeError, AttributeError):
            pass
    
    def _display_error(self, error: str) -> None:
        from gui.theme import TEXT_WARNING
        try:
            self._clear_scroll_frame()
            ctk.CTkLabel(
                self.scroll_frame,
                text=f"⚠ Error: {error}",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_WARNING
            ).pack(pady=40)
        except (RuntimeError, AttributeError):
            pass
