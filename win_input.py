"""
Windows Input Simulator & Focus Manager for TouchKey POS Pro.
Full Hardware Scan Code + Unicode Support for POS Systems (RPOS, iiko, r_keeper, etc.).
"""

import sys
import os
import ctypes
from ctypes import wintypes
import time
import winreg

from PyQt6.QtWidgets import QApplication

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Virtual Key Codes
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_CAPITAL = 0x14
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_DELETE = 0x2E
VK_OEM_PERIOD = 0xBE
VK_OEM_COMMA = 0xBC

KEYEVENTF_KEYUP = 0x0002

# Window Styles
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008

HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SW_HIDE = 0

# Set 64-bit safe prototypes
user32.SetWindowPos.argtypes = [
    wintypes.HWND, wintypes.HWND,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.UINT
]
user32.SetWindowPos.restype = wintypes.BOOL

user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND

user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL

user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL

user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, ctypes.c_size_t]
user32.keybd_event.restype = None

user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT

if hasattr(user32, 'GetWindowLongPtrW'):
    user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
    user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
else:
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
    user32.SetWindowLongW.restype = ctypes.c_long


def send_digit_or_char(char: str):
    """
    Sends digits via hardware scan codes (for masked price/quantity fields),
    and Unicode text via direct clipboard paste (for search/names).
    """
    if not char:
        return

    if char == "00":
        send_digit_or_char("0")
        send_digit_or_char("0")
    elif len(char) == 1 and char.isdigit():
        vk = ord(char)
        scan = user32.MapVirtualKeyW(vk, 0)
        user32.keybd_event(vk, scan, 0, 0)
        time.sleep(0.015)
        user32.keybd_event(vk, scan, KEYEVENTF_KEYUP, 0)
        time.sleep(0.010)
    elif char == ".":
        vk = VK_OEM_PERIOD
        scan = user32.MapVirtualKeyW(vk, 0)
        user32.keybd_event(vk, scan, 0, 0)
        time.sleep(0.015)
        user32.keybd_event(vk, scan, KEYEVENTF_KEYUP, 0)
        time.sleep(0.010)
    elif char == "+":
        send_unicode_char("+")
    elif char == "-":
        send_unicode_char("-")
    else:
        send_unicode_char(char)


def send_unicode_char(char: str):
    """Sends text / letters via instant Unicode paste."""
    if not char:
        return
    if char == " ":
        send_vk_key(VK_SPACE)
        return

    app = QApplication.instance()
    if app:
        app.clipboard().setText(char)
        time.sleep(0.005)
        scan_ctrl = user32.MapVirtualKeyW(VK_CONTROL, 0)
        scan_v = user32.MapVirtualKeyW(ord('V'), 0)
        user32.keybd_event(VK_CONTROL, scan_ctrl, 0, 0)
        time.sleep(0.005)
        user32.keybd_event(ord('V'), scan_v, 0, 0)
        time.sleep(0.012)
        user32.keybd_event(ord('V'), scan_v, KEYEVENTF_KEYUP, 0)
        time.sleep(0.005)
        user32.keybd_event(VK_CONTROL, scan_ctrl, KEYEVENTF_KEYUP, 0)
        time.sleep(0.005)


def send_text(text: str):
    """Sends multi-character strings."""
    if not text:
        return
    if text.isdigit() or text == "00":
        for ch in text:
            send_digit_or_char(ch)
    else:
        send_unicode_char(text)


def send_vk_key(vk_code: int):
    """Sends a virtual key code with hardware scan code."""
    scan = user32.MapVirtualKeyW(vk_code, 0)
    user32.keybd_event(vk_code, scan, 0, 0)
    time.sleep(0.015)
    user32.keybd_event(vk_code, scan, KEYEVENTF_KEYUP, 0)
    time.sleep(0.010)


def send_backspace(count: int = 1):
    """
    Sends Backspace with hardware scan code (0x0E).
    Works on both standard text fields and masked POS price inputs.
    """
    scan = user32.MapVirtualKeyW(VK_BACK, 0) # 0x0E
    for _ in range(count):
        user32.keybd_event(VK_BACK, scan, 0, 0)
        time.sleep(0.015)
        user32.keybd_event(VK_BACK, scan, KEYEVENTF_KEYUP, 0)
        time.sleep(0.010)


def send_enter():
    """Sends Enter key."""
    send_vk_key(VK_RETURN)


def send_tab():
    """Sends Tab key."""
    send_vk_key(VK_TAB)


def send_escape():
    """Sends Escape key."""
    send_vk_key(VK_ESCAPE)


def send_select_all_and_clear():
    """
    Clears active field completely:
    1. Sends Ctrl+A + Backspace (for standard text & search fields).
    2. Sends burst of Backspaces + Delete with hardware scan codes (for masked POS price/currency fields).
    """
    scan_ctrl = user32.MapVirtualKeyW(VK_CONTROL, 0)
    scan_a = user32.MapVirtualKeyW(ord('A'), 0)
    scan_back = user32.MapVirtualKeyW(VK_BACK, 0) # 0x0E
    scan_del = user32.MapVirtualKeyW(VK_DELETE, 0) # 0x53

    # Step 1: Ctrl+A + Backspace
    user32.keybd_event(VK_CONTROL, scan_ctrl, 0, 0)
    time.sleep(0.015)
    user32.keybd_event(ord('A'), scan_a, 0, 0)
    time.sleep(0.015)
    user32.keybd_event(ord('A'), scan_a, KEYEVENTF_KEYUP, 0)
    time.sleep(0.015)
    user32.keybd_event(VK_CONTROL, scan_ctrl, KEYEVENTF_KEYUP, 0)
    time.sleep(0.020)

    user32.keybd_event(VK_BACK, scan_back, 0, 0)
    time.sleep(0.015)
    user32.keybd_event(VK_BACK, scan_back, KEYEVENTF_KEYUP, 0)
    time.sleep(0.015)

    # Step 2: Multi-backspace for masked numeric fields (wipes price down to 0)
    for _ in range(10):
        user32.keybd_event(VK_BACK, scan_back, 0, 0)
        time.sleep(0.005)
        user32.keybd_event(VK_BACK, scan_back, KEYEVENTF_KEYUP, 0)
        time.sleep(0.005)


def apply_window_no_focus_and_topmost(hwnd: int):
    """Ensures window never steals focus and stays always on top."""
    try:
        if hasattr(user32, 'GetWindowLongPtrW'):
            current_style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
            new_style = current_style | WS_EX_NOACTIVATE | WS_EX_TOPMOST
            user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, new_style)
        else:
            current_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_style = current_style | WS_EX_NOACTIVATE | WS_EX_TOPMOST
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)

        user32.SetWindowPos(
            hwnd,
            HWND_TOPMOST,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
        )
    except Exception as e:
        print(f"apply_window_no_focus_and_topmost error: {e}")


def suppress_windows_tabtip():
    """Suppresses standard Windows TabTip keyboard window."""
    try:
        hwnd = user32.FindWindowW("IPTip_Main_Window", None)
        if hwnd:
            user32.ShowWindow(hwnd, SW_HIDE)
            user32.PostMessageW(hwnd, 0x0010, 0, 0)
    except Exception:
        pass


def configure_windows_registry_no_tabtip():
    """Sets registry flag to disable Windows touch keyboard auto-invoke."""
    try:
        key_path = r"Software\Microsoft\TabletTip\1.7"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "EnableDesktopModeAutoInvoke", 0, winreg.REG_DWORD, 0)
    except Exception:
        pass
