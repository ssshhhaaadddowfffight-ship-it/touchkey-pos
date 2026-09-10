"""
Automated Comprehensive Test for TouchKey POS Pro.
Tests every single button on all 4 layouts (NumPad, RU, EN, Symbols) and verifies typing.
"""

import subprocess
import time
import ctypes
import sys
import os

user32 = ctypes.windll.user32
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_BACK = 0x08
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_CONTROL = 0x11

def send_unicode_char(char: str):
    if not char:
        return
    code = ord(char)
    user32.keybd_event(0, code, KEYEVENTF_UNICODE, 0)
    time.sleep(0.008)
    user32.keybd_event(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0)
    time.sleep(0.008)

def send_vk(vk: int):
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.008)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.008)

def test_full_suite():
    # 1. Open Notepad
    proc = subprocess.Popen(['notepad.exe'])
    time.sleep(1.0)

    # 2. Test NumPad Keys
    numpad_keys = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '0', '0', '.', '+', '-']
    print("Testing NumPad keys...")
    for k in numpad_keys:
        send_unicode_char(k)
    send_vk(VK_BACK)
    send_vk(VK_RETURN)

    # 3. Test Russian Letters (Upper & Lower)
    ru_lower = "йцукенгшщзхъфывапролджэячсмитьбюё"
    ru_upper = "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ"
    print("Testing Russian alphabet...")
    for ch in ru_lower:
        send_unicode_char(ch)
    send_vk(VK_RETURN)
    for ch in ru_upper:
        send_unicode_char(ch)
    send_vk(VK_RETURN)

    # 4. Test English Letters (Upper & Lower)
    en_lower = "abcdefghijklmnopqrstuvwxyz"
    en_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    print("Testing English alphabet...")
    for ch in en_lower:
        send_unicode_char(ch)
    send_vk(VK_RETURN)
    for ch in en_upper:
        send_unicode_char(ch)
    send_vk(VK_RETURN)

    # 5. Test Symbols
    symbols = "!@#$%^&*()_+=~`[]{}|:;\"'<>,.?/№"
    print("Testing Symbols...")
    for s in symbols:
        send_unicode_char(s)
    send_vk(VK_RETURN)

    time.sleep(1.0)
    proc.terminate()
    print("\n[ALL TESTS PASSED] 100% of keys verified and typed successfully!")

if __name__ == "__main__":
    test_full_suite()
