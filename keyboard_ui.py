"""
TouchKey POS Pro — Universal Touch Virtual Keyboard UI (PyQt6).
Designed for restaurant POS systems on Touch Monoblocks.
"""

import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QCursor, QIcon, QPainter, QBrush, QPen
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QStackedWidget, QLabel, QFrame, QSizePolicy
)

from win_input import (
    send_unicode_char, send_text, send_digit_or_char, send_backspace, send_enter,
    send_tab, send_escape, send_select_all_and_clear,
    apply_window_no_focus_and_topmost
)


class TouchButton(QPushButton):
    """High contrast touch-friendly button with active feedback."""
    def __init__(self, text: str, parent=None, role: str = "normal", font_scale: float = 1.0):
        super().__init__(text, parent)
        self.role = role
        self.font_scale = font_scale
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update_style()

    def update_style(self, base_font_size: int = 18, border_radius: int = 10):
        actual_font_size = max(13, int(base_font_size * self.font_scale))
        
        if self.role == "primary_enter":
            bg = "#27ae60"
            bg_hover = "#2ecc71"
            bg_pressed = "#1e8449"
            color = "#ffffff"
            border = "#2ecc71"
        elif self.role == "danger_backspace":
            bg = "#c0392b"
            bg_hover = "#e74c3c"
            bg_pressed = "#922b21"
            color = "#ffffff"
            border = "#e74c3c"
        elif self.role == "clear":
            bg = "#d35400"
            bg_hover = "#e67e22"
            bg_pressed = "#a04000"
            color = "#ffffff"
            border = "#e67e22"
        elif self.role == "action_mode":
            bg = "#2c3e50"
            bg_hover = "#34495e"
            bg_pressed = "#1a252f"
            color = "#ecf0f1"
            border = "#4b6584"
        elif self.role == "number":
            bg = "#2b2f3a"
            bg_hover = "#3d4251"
            bg_pressed = "#1e2129"
            color = "#ffffff"
            border = "#3e4453"
        elif self.role == "space":
            bg = "#242831"
            bg_hover = "#353b49"
            bg_pressed = "#191c22"
            color = "#bdc3c7"
            border = "#3a404f"
        else:
            bg = "#242831"
            bg_hover = "#373e4d"
            bg_pressed = "#1a1c23"
            color = "#f5f6fa"
            border = "#383f4e"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
                font-size: {actual_font_size}px;
                font-weight: bold;
                border: 2px solid {border};
                border-radius: {border_radius}px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
                border-color: #00d2ff;
            }}
            QPushButton:pressed {{
                background-color: {bg_pressed};
                padding-top: 6px;
                padding-left: 5px;
            }}
        """)


class FloatingTogglePill(QWidget):
    """Floating pill button in corner to quickly show/hide keyboard."""
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setFixedSize(140, 50)
        self.drag_position = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn = QPushButton("⌨️ Клавиатура", self)
        self.btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e3c72, stop:1 #2a5298);
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #00d2ff;
                border-radius: 25px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background: #2a5298;
                border-color: #ffffff;
            }
            QPushButton:pressed {
                background: #14284b;
            }
        """)
        self.btn.clicked.connect(self.clicked.emit)
        layout.addWidget(self.btn)

    def showEvent(self, event):
        super().showEvent(event)
        apply_window_no_focus_and_topmost(int(self.winId()))


class TouchKeyPOSKeyboard(QWidget):
    """Main Touch Virtual Keyboard Window."""

    def __init__(self):
        super().__init__()
        
        self.current_scale = 1.30
        self.shift_active = False
        self.current_layout_name = "numpad"

        self.all_buttons: list[TouchButton] = []
        self.drag_position = None

        self.init_window_properties()
        self.init_ui()
        self.apply_scale()

    def init_window_properties(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setWindowTitle("TouchKey POS Pro")

    def showEvent(self, event):
        super().showEvent(event)
        apply_window_no_focus_and_topmost(int(self.winId()))

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Outer Container
        self.container = QFrame(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QFrame#container {
                background-color: #15171e;
                border: 2px solid #2b303d;
                border-radius: 16px;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 10, 12, 12)
        container_layout.setSpacing(8)

        # 1. Header with Mode Controls & Scaling
        self.top_bar = self.create_top_bar()
        container_layout.addWidget(self.top_bar)

        # 2. Stacked Pages
        self.stacked_pages = QStackedWidget(self)
        
        self.numpad_page = self.create_numpad_page()
        self.ru_page = self.create_ru_keyboard_page()
        self.en_page = self.create_en_keyboard_page()
        self.sym_page = self.create_symbols_page()

        self.stacked_pages.addWidget(self.numpad_page)    # 0: NumPad
        self.stacked_pages.addWidget(self.ru_page)        # 1: RU
        self.stacked_pages.addWidget(self.en_page)        # 2: EN
        self.stacked_pages.addWidget(self.sym_page)       # 3: Symbols

        container_layout.addWidget(self.stacked_pages, 1)
        main_layout.addWidget(self.container)

    def create_top_bar(self) -> QWidget:
        header = QFrame(self)
        header.setFixedHeight(48)
        header.setStyleSheet("""
            QFrame {
                background-color: #1d212b;
                border-radius: 10px;
                border: 1px solid #2c3242;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 4, 10, 4)
        h_layout.setSpacing(8)

        # Title
        self.title_label = QLabel("✨ TOUCHKEY POS", header)
        self.title_label.setStyleSheet("""
            color: #00d2ff;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 0.5px;
        """)
        h_layout.addWidget(self.title_label)

        h_layout.addStretch(1)

        # Mode Buttons
        self.btn_mode_num = QPushButton("🔢 Касса (NumPad)", header)
        self.btn_mode_ru = QPushButton("🔤 Русский (RU)", header)
        self.btn_mode_en = QPushButton("🌐 English (EN)", header)

        for btn in [self.btn_mode_num, self.btn_mode_ru, self.btn_mode_en]:
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setFixedHeight(36)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #282d3b;
                    color: #d1d5db;
                    font-size: 13px;
                    font-weight: bold;
                    border: 1px solid #3c4458;
                    border-radius: 8px;
                    padding: 0 12px;
                }
                QPushButton:hover {
                    background-color: #3b4358;
                    color: #ffffff;
                }
            """)

        self.btn_mode_num.clicked.connect(lambda: self.switch_mode("numpad"))
        self.btn_mode_ru.clicked.connect(lambda: self.switch_mode("ru"))
        self.btn_mode_en.clicked.connect(lambda: self.switch_mode("en"))

        h_layout.addWidget(self.btn_mode_num)
        h_layout.addWidget(self.btn_mode_ru)
        h_layout.addWidget(self.btn_mode_en)

        # Scale Buttons
        self.btn_scale_down = QPushButton("А -", header)
        self.btn_scale_up = QPushButton("А +", header)
        for s_btn in [self.btn_scale_down, self.btn_scale_up]:
            s_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            s_btn.setFixedSize(38, 36)
            s_btn.setStyleSheet("""
                QPushButton {
                    background-color: #242936;
                    color: #00d2ff;
                    font-size: 13px;
                    font-weight: bold;
                    border: 1px solid #34495e;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #2f384a;
                    color: #ffffff;
                }
            """)

        self.btn_scale_down.clicked.connect(self.scale_down)
        self.btn_scale_up.clicked.connect(self.scale_up)

        h_layout.addWidget(self.btn_scale_down)
        h_layout.addWidget(self.btn_scale_up)

        # Minimize Button
        self.btn_minimize = QPushButton("🗕", header)
        self.btn_minimize.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_minimize.setFixedSize(38, 36)
        self.btn_minimize.setStyleSheet("""
            QPushButton {
                background-color: #282d3b;
                color: #95a5a6;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #3c4458;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3b4358;
                color: #ffffff;
            }
        """)
        self.btn_minimize.clicked.connect(self.hide)
        h_layout.addWidget(self.btn_minimize)

        return header

    # ==========================
    # 1. POS NUMPAD (Касса)
    # ==========================
    def create_numpad_page(self) -> QWidget:
        page = QWidget()
        layout = QGridLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        def make_btn(text, role="number", font_scale=1.3):
            btn = TouchButton(text, role=role, font_scale=font_scale)
            self.all_buttons.append(btn)
            return btn

        # Row 0: 7, 8, 9, Backspace, Clear
        b7 = make_btn("7")
        b7.clicked.connect(lambda: send_digit_or_char("7"))
        b8 = make_btn("8")
        b8.clicked.connect(lambda: send_digit_or_char("8"))
        b9 = make_btn("9")
        b9.clicked.connect(lambda: send_digit_or_char("9"))
        b_bs = make_btn("⌫ Стереть", role="danger_backspace", font_scale=1.1)
        b_bs.clicked.connect(lambda: send_backspace(1))
        b_clr = make_btn("Очистить (C)", role="clear", font_scale=1.0)
        b_clr.clicked.connect(send_select_all_and_clear)

        layout.addWidget(b7, 0, 0)
        layout.addWidget(b8, 0, 1)
        layout.addWidget(b9, 0, 2)
        layout.addWidget(b_bs, 0, 3)
        layout.addWidget(b_clr, 0, 4)

        # Row 1: 4, 5, 6, Tab, Esc
        b4 = make_btn("4")
        b4.clicked.connect(lambda: send_digit_or_char("4"))
        b5 = make_btn("5")
        b5.clicked.connect(lambda: send_digit_or_char("5"))
        b6 = make_btn("6")
        b6.clicked.connect(lambda: send_digit_or_char("6"))
        b_tab = make_btn("⇥ След. поле", role="action_mode", font_scale=1.0)
        b_tab.clicked.connect(send_tab)
        b_esc = make_btn("✕ Отмена", role="action_mode", font_scale=1.0)
        b_esc.clicked.connect(send_escape)

        layout.addWidget(b4, 1, 0)
        layout.addWidget(b5, 1, 1)
        layout.addWidget(b6, 1, 2)
        layout.addWidget(b_tab, 1, 3)
        layout.addWidget(b_esc, 1, 4)

        # Row 2: 1, 2, 3, +, -
        b1 = make_btn("1")
        b1.clicked.connect(lambda: send_digit_or_char("1"))
        b2 = make_btn("2")
        b2.clicked.connect(lambda: send_digit_or_char("2"))
        b3 = make_btn("3")
        b3.clicked.connect(lambda: send_digit_or_char("3"))
        b_plus = make_btn("+", role="action_mode", font_scale=1.4)
        b_plus.clicked.connect(lambda: send_digit_or_char("+"))
        b_minus = make_btn("-", role="action_mode", font_scale=1.4)
        b_minus.clicked.connect(lambda: send_digit_or_char("-"))

        layout.addWidget(b1, 2, 0)
        layout.addWidget(b2, 2, 1)
        layout.addWidget(b3, 2, 2)
        layout.addWidget(b_plus, 2, 3)
        layout.addWidget(b_minus, 2, 4)

        # Row 3: 0, 00, ., ВВОД / ГОТОВО
        b0 = make_btn("0")
        b0.clicked.connect(lambda: send_digit_or_char("0"))
        b00 = make_btn("00")
        b00.clicked.connect(lambda: send_digit_or_char("00"))
        b_dot = make_btn(".", font_scale=1.4)
        b_dot.clicked.connect(lambda: send_digit_or_char("."))
        b_enter = make_btn("↵ ВВОД / СОХРАНИТЬ", role="primary_enter", font_scale=1.2)
        b_enter.clicked.connect(send_enter)

        layout.addWidget(b0, 3, 0)
        layout.addWidget(b00, 3, 1)
        layout.addWidget(b_dot, 3, 2)
        layout.addWidget(b_enter, 3, 3, 1, 2)

        return page

    # =================================
    # 2. RUSSIAN KEYBOARD (Русский)
    # =================================
    def create_ru_keyboard_page(self) -> QWidget:
        page = QWidget()
        v_layout = QVBoxLayout(page)
        v_layout.setContentsMargins(2, 2, 2, 2)
        v_layout.setSpacing(6)

        row0 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "⌫"]
        row1 = ["Й", "Ц", "У", "К", "Е", "Н", "Г", "Ш", "Щ", "З", "Х", "Ъ"]
        row2 = ["Ф", "Ы", "В", "А", "П", "Р", "О", "Л", "Д", "Ж", "Э"]
        row3 = ["⇧ SHIFT", "Я", "Ч", "С", "М", "И", "Т", "Ь", "Б", "Ю", ".", ","]

        v_layout.addLayout(self._build_key_row(row0))
        v_layout.addLayout(self._build_key_row(row1))
        v_layout.addLayout(self._build_key_row(row2))
        v_layout.addLayout(self._build_key_row(row3))

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(6)

        btn_num = TouchButton("🔢 123", role="action_mode", font_scale=1.0)
        btn_num.clicked.connect(lambda: self.switch_mode("numpad"))
        self.all_buttons.append(btn_num)
        bottom_layout.addWidget(btn_num, 2)

        btn_lang = TouchButton("🌐 ENG", role="action_mode", font_scale=1.0)
        btn_lang.clicked.connect(lambda: self.switch_mode("en"))
        self.all_buttons.append(btn_lang)
        bottom_layout.addWidget(btn_lang, 2)

        btn_sym = TouchButton("? # !", role="action_mode", font_scale=1.0)
        btn_sym.clicked.connect(lambda: self.switch_mode("symbols"))
        self.all_buttons.append(btn_sym)
        bottom_layout.addWidget(btn_sym, 2)

        btn_space = TouchButton("П Р О Б Е Л", role="space", font_scale=1.0)
        btn_space.clicked.connect(lambda: send_unicode_char(" "))
        self.all_buttons.append(btn_space)
        bottom_layout.addWidget(btn_space, 8)

        btn_enter = TouchButton("↵ ВВОД", role="primary_enter", font_scale=1.1)
        btn_enter.clicked.connect(send_enter)
        self.all_buttons.append(btn_enter)
        bottom_layout.addWidget(btn_enter, 3)

        v_layout.addLayout(bottom_layout)
        return page

    # =================================
    # 3. ENGLISH KEYBOARD (English)
    # =================================
    def create_en_keyboard_page(self) -> QWidget:
        page = QWidget()
        v_layout = QVBoxLayout(page)
        v_layout.setContentsMargins(2, 2, 2, 2)
        v_layout.setSpacing(6)

        row0 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "⌫"]
        row1 = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
        row2 = ["A", "S", "D", "F", "G", "H", "J", "K", "L"]
        row3 = ["⇧ SHIFT", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "?"]

        v_layout.addLayout(self._build_key_row(row0))
        v_layout.addLayout(self._build_key_row(row1))
        v_layout.addLayout(self._build_key_row(row2))
        v_layout.addLayout(self._build_key_row(row3))

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(6)

        btn_num = TouchButton("🔢 123", role="action_mode", font_scale=1.0)
        btn_num.clicked.connect(lambda: self.switch_mode("numpad"))
        self.all_buttons.append(btn_num)
        bottom_layout.addWidget(btn_num, 2)

        btn_lang = TouchButton("🌐 РУС", role="action_mode", font_scale=1.0)
        btn_lang.clicked.connect(lambda: self.switch_mode("ru"))
        self.all_buttons.append(btn_lang)
        bottom_layout.addWidget(btn_lang, 2)

        btn_sym = TouchButton("? # !", role="action_mode", font_scale=1.0)
        btn_sym.clicked.connect(lambda: self.switch_mode("symbols"))
        self.all_buttons.append(btn_sym)
        bottom_layout.addWidget(btn_sym, 2)

        btn_space = TouchButton("S P A C E", role="space", font_scale=1.0)
        btn_space.clicked.connect(lambda: send_unicode_char(" "))
        self.all_buttons.append(btn_space)
        bottom_layout.addWidget(btn_space, 8)

        btn_enter = TouchButton("↵ ENTER", role="primary_enter", font_scale=1.1)
        btn_enter.clicked.connect(send_enter)
        self.all_buttons.append(btn_enter)
        bottom_layout.addWidget(btn_enter, 3)

        v_layout.addLayout(bottom_layout)
        return page

    # =================================
    # 4. SYMBOLS PAGE
    # =================================
    def create_symbols_page(self) -> QWidget:
        page = QWidget()
        v_layout = QVBoxLayout(page)
        v_layout.setContentsMargins(2, 2, 2, 2)
        v_layout.setSpacing(6)

        row1 = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "⌫"]
        row2 = ["`", "~", "_", "+", "=", "[", "]", "{", "}", "\\", "|"]
        row3 = [":", ";", "\"", "'", "<", ">", ",", ".", "?", "/", "№"]

        v_layout.addLayout(self._build_key_row(row1))
        v_layout.addLayout(self._build_key_row(row2))
        v_layout.addLayout(self._build_key_row(row3))

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(6)

        btn_num = TouchButton("🔢 NumPad", role="action_mode", font_scale=1.0)
        btn_num.clicked.connect(lambda: self.switch_mode("numpad"))
        self.all_buttons.append(btn_num)
        bottom_layout.addWidget(btn_num, 3)

        btn_ru = TouchButton("🔤 РУС", role="action_mode", font_scale=1.0)
        btn_ru.clicked.connect(lambda: self.switch_mode("ru"))
        self.all_buttons.append(btn_ru)
        bottom_layout.addWidget(btn_ru, 3)

        btn_space = TouchButton("ПРОБЕЛ", role="space", font_scale=1.0)
        btn_space.clicked.connect(lambda: send_unicode_char(" "))
        self.all_buttons.append(btn_space)
        bottom_layout.addWidget(btn_space, 8)

        btn_enter = TouchButton("↵ ВВОД", role="primary_enter", font_scale=1.1)
        btn_enter.clicked.connect(send_enter)
        self.all_buttons.append(btn_enter)
        bottom_layout.addWidget(btn_enter, 3)

        v_layout.addLayout(bottom_layout)
        return page

    def _build_key_row(self, keys: list[str]) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(6)

        for key in keys:
            if key == "⌫":
                btn = TouchButton("⌫", role="danger_backspace", font_scale=1.2)
                btn.clicked.connect(lambda: send_backspace(1))
                layout.addWidget(btn, 2)
            elif "SHIFT" in key:
                btn = TouchButton(key, role="action_mode", font_scale=0.9)
                btn.clicked.connect(self.toggle_shift)
                layout.addWidget(btn, 2)
            else:
                btn = TouchButton(key, role="normal", font_scale=1.1)
                btn.clicked.connect(lambda checked=False, k=key: self.on_char_key_pressed(k))
                layout.addWidget(btn, 1)

            self.all_buttons.append(btn)

        return layout

    def on_char_key_pressed(self, char: str):
        if len(char) == 1:
            if self.shift_active:
                send_unicode_char(char.upper())
                self.toggle_shift()
            else:
                send_unicode_char(char.lower())
        else:
            send_text(char)

    def toggle_shift(self):
        self.shift_active = not self.shift_active
        for btn in self.all_buttons:
            t = btn.text()
            if len(t) == 1 and t.isalpha():
                btn.setText(t.upper() if self.shift_active else t.lower())

    def switch_mode(self, mode: str):
        self.current_layout_name = mode
        if mode == "numpad":
            self.stacked_pages.setCurrentIndex(0)
            self.title_label.setText("🔢 TOUCHKEY POS • КАЛЬКУЛЯТОР")
            self.btn_mode_num.setStyleSheet("background-color: #00d2ff; color: #000000; font-weight: bold; border-radius: 8px;")
            self.btn_mode_ru.setStyleSheet("background-color: #282d3b; color: #d1d5db; font-weight: bold; border-radius: 8px;")
            self.btn_mode_en.setStyleSheet("background-color: #282d3b; color: #d1d5db; font-weight: bold; border-radius: 8px;")
        elif mode == "ru":
            self.stacked_pages.setCurrentIndex(1)
            self.title_label.setText("🔤 TOUCHKEY POS • РУССКИЙ ПОИСК")
            self.btn_mode_num.setStyleSheet("background-color: #282d3b; color: #d1d5db; font-weight: bold; border-radius: 8px;")
            self.btn_mode_ru.setStyleSheet("background-color: #00d2ff; color: #000000; font-weight: bold; border-radius: 8px;")
            self.btn_mode_en.setStyleSheet("background-color: #282d3b; color: #d1d5db; font-weight: bold; border-radius: 8px;")
        elif mode == "en":
            self.stacked_pages.setCurrentIndex(2)
            self.title_label.setText("🌐 TOUCHKEY POS • ENGLISH SEARCH")
            self.btn_mode_num.setStyleSheet("background-color: #282d3b; color: #d1d5db; font-weight: bold; border-radius: 8px;")
            self.btn_mode_ru.setStyleSheet("background-color: #282d3b; color: #d1d5db; font-weight: bold; border-radius: 8px;")
            self.btn_mode_en.setStyleSheet("background-color: #00d2ff; color: #000000; font-weight: bold; border-radius: 8px;")
        elif mode == "symbols":
            self.stacked_pages.setCurrentIndex(3)
            self.title_label.setText("✨ TOUCHKEY POS • СИМВОЛЫ")

        self.apply_scale()

    def scale_up(self):
        if self.current_scale < 2.0:
            self.current_scale += 0.15
            self.apply_scale()

    def scale_down(self):
        if self.current_scale > 0.8:
            self.current_scale -= 0.15
            self.apply_scale()

    def apply_scale(self):
        if self.current_layout_name == "numpad":
            base_w = 700
            base_h = 370
        else:
            base_w = 900
            base_h = 400

        w = int(base_w * self.current_scale)
        h = int(base_h * self.current_scale)
        self.resize(w, h)

        base_font = int(16 * self.current_scale)
        radius = max(6, int(8 * self.current_scale))

        for btn in self.all_buttons:
            btn.update_style(base_font_size=base_font, border_radius=radius)

        self.position_at_bottom_center()

    def position_at_bottom_center(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
            y = screen_geo.y() + screen_geo.height() - self.height() - 15
            self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
