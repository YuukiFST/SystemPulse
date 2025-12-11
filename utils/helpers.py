import sys
import tempfile
import shutil
import ctypes
from pathlib import Path
from typing import Optional


def get_resource_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "winforge" / "resources"
    return Path(__file__).parent.parent / "resources"


def get_temp_dir() -> Path:
    temp_dir = Path(tempfile.gettempdir()) / "WinForge"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir


def extract_tools() -> Path:
    resource_path = get_resource_path()
    temp_dir = get_temp_dir()
    tools = ["DevManView.exe", "DeviceCleanupCmd.exe"]
    for tool in tools:
        src = resource_path / tool
        dst = temp_dir / tool
        if src.exists() and not dst.exists():
            try:
                shutil.copy2(src, dst)
            except (IOError, OSError, shutil.Error):
                pass
    return temp_dir


def cleanup_temp() -> None:
    temp_dir = get_temp_dir()
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
        except (IOError, OSError, shutil.Error):
            pass


def set_window_icon(window) -> None:
    try:
        from PIL import Image, ImageTk
        res_path = get_resource_path()
        
        icon_ico = res_path / "icon.ico"
        icon_png = res_path / "icon.png"

        def _apply_icon():
            _set_tkinter_icon(window, icon_ico)
            _set_photo_icon(window, icon_png, icon_ico)
            _set_native_icon(window, icon_ico)

        _apply_icon()
        window.after(200, _apply_icon)
            
    except (ImportError, FileNotFoundError, OSError):
        pass


def _set_tkinter_icon(window, icon_ico: Path) -> None:
    try:
        if icon_ico.exists():
            window.iconbitmap(str(icon_ico))
    except (RuntimeError, OSError):
        pass


def _set_photo_icon(window, icon_png: Path, icon_ico: Path) -> None:
    try:
        from PIL import Image, ImageTk
        icon_path = icon_png if icon_png.exists() else (icon_ico if icon_ico.exists() else None)
        if icon_path:
            img = Image.open(icon_path)
            window.iconphoto(False, ImageTk.PhotoImage(img))
    except (ImportError, FileNotFoundError, OSError, RuntimeError):
        pass


def _set_native_icon(window, icon_ico: Path) -> None:
    try:
        if not icon_ico.exists():
            return
            
        window.update_idletasks()
        hwnd = window.winfo_id()
        
        if not hwnd:
            return
            
        WM_SETICON = 0x80
        ICON_SMALL = 0
        ICON_BIG = 1
        LR_LOADFROMFILE = 0x10
        IMAGE_ICON = 1
        
        hIconBig = ctypes.windll.user32.LoadImageW(
            None, str(icon_ico), IMAGE_ICON, 0, 0, LR_LOADFROMFILE
        )
        if hIconBig:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hIconBig)
            
        hIconSmall = ctypes.windll.user32.LoadImageW(
            None, str(icon_ico), IMAGE_ICON, 0, 0, LR_LOADFROMFILE
        )
        if hIconSmall:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hIconSmall)
    except (OSError, RuntimeError, AttributeError):
        pass
