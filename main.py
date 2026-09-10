"""
TouchKey POS Pro — Main Entry Point with System Tray and TabTip Auto-Suppressor.
"""

import sys
import os
import traceback

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from keyboard_ui import TouchKeyPOSKeyboard, FloatingTogglePill
from win_input import suppress_windows_tabtip, configure_windows_registry_no_tabtip


def exception_hook(exctype, value, tb):
    """Logs any uncaught exceptions to error.log instead of silently dying."""
    err_text = "".join(traceback.format_exception(exctype, value, tb))
    print("UNCAUGHT EXCEPTION:", err_text)
    try:
        log_path = os.path.join(CURRENT_DIR, "keyboard_crash.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(err_text + "\n" + "=" * 50 + "\n")
    except Exception:
        pass
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook


def get_app_icon() -> QIcon:
    for filename in ["app_icon.ico", "app_icon.png"]:
        p = os.path.join(CURRENT_DIR, filename)
        if os.path.exists(p):
            return QIcon(p)
    return QIcon()


class TouchKeyApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.icon = get_app_icon()
        self.app.setWindowIcon(self.icon)

        # 1. Disable Windows TabTip in registry
        configure_windows_registry_no_tabtip()

        # 2. Main Keyboard Overlay Window
        self.keyboard = TouchKeyPOSKeyboard()

        # 3. Floating Quick Toggle Pill
        self.floating_pill = FloatingTogglePill()
        self.floating_pill.clicked.connect(self.toggle_keyboard)

        # 4. System Tray
        self.init_tray()

        # 5. Position & Show Floating Pill only (Keyboard starts minimized)
        self.position_floating_pill()
        self.floating_pill.show()

        # 6. Periodic TabTip suppressor timer (every 300ms)
        self.tabtip_timer = QTimer()
        self.tabtip_timer.timeout.connect(suppress_windows_tabtip)
        self.tabtip_timer.start(300)

    def position_floating_pill(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = screen_geo.x() + screen_geo.width() - self.floating_pill.width() - 25
            y = screen_geo.y() + screen_geo.height() - self.floating_pill.height() - 25
            self.floating_pill.move(x, y)

    def init_tray(self):
        self.tray = QSystemTrayIcon(self.icon, self.app)
        self.tray.setToolTip("TouchKey POS Pro")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e212b;
                color: #ffffff;
                border: 1px solid #3c4458;
                font-family: 'Segoe UI';
                font-size: 13px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #00d2ff;
                color: #000000;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3c4458;
                margin: 4px 0;
            }
        """)

        act_toggle = QAction("⌨️ Показать / Скрыть клавиатуру", menu)
        act_toggle.triggered.connect(self.toggle_keyboard)
        menu.addAction(act_toggle)

        menu.addSeparator()

        act_num = QAction("🔢 Режим NumPad (Касса)", menu)
        act_num.triggered.connect(lambda: (self.keyboard.switch_mode("numpad"), self.keyboard.show()))
        menu.addAction(act_num)

        act_ru = QAction("🔤 Русский поиск (RU)", menu)
        act_ru.triggered.connect(lambda: (self.keyboard.switch_mode("ru"), self.keyboard.show()))
        menu.addAction(act_ru)

        act_en = QAction("🌐 English search (EN)", menu)
        act_en.triggered.connect(lambda: (self.keyboard.switch_mode("en"), self.keyboard.show()))
        menu.addAction(act_en)

        menu.addSeparator()

        act_scale_up = QAction("🔍 Увеличить размер (А +)", menu)
        act_scale_up.triggered.connect(self.keyboard.scale_up)
        menu.addAction(act_scale_up)

        act_scale_down = QAction("🔍 Уменьшить размер (А -)", menu)
        act_scale_down.triggered.connect(self.keyboard.scale_down)
        menu.addAction(act_scale_down)

        menu.addSeparator()

        act_exit = QAction("❌ Выход", menu)
        act_exit.triggered.connect(self.app.quit)
        menu.addAction(act_exit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_keyboard()

    def toggle_keyboard(self):
        if self.keyboard.isVisible():
            self.keyboard.hide()
        else:
            self.keyboard.show()
            self.keyboard.position_at_bottom_center()

    def run(self):
        return self.app.exec()


def main():
    app = TouchKeyApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
