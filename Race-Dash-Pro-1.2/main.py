#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import signal
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt

from utils.swipe_container import SwipeContainer
from controllers.navigation import NavigationController
from screens.demo_screen import DemoScreen
from screens.logs_screen import LogsScreen
from screens.graphs_screen import GraphsScreen
from rgb.rgb_controller import RGBController

# Глобальная переменная для RGB
_rgb = None

def get_rgb():
    global _rgb
    if _rgb is None:
        _rgb = RGBController()
    return _rgb

def cleanup_rgb():
    """Принудительное выключение ленты"""
    global _rgb
    if _rgb is not None:
        print("🛑 Выключение RGB-ленты...")
        _rgb.cleanup()
        _rgb = None
    # Дополнительная очистка — пробуем выключить через прямой доступ
    try:
        import board
        import neopixel
        pin = getattr(board, 'D18')
        pixels = neopixel.NeoPixel(pin, 29, brightness=0.5)
        for i in range(29):
            pixels[i] = 0
        pixels.show()
        pixels.deinit()
    except:
        pass

# Обработчики сигналов
def signal_handler(sig, frame):
    print(f"\n🛑 Сигнал {sig} получен...")
    cleanup_rgb()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RACE DASH PRO")
        self.setGeometry(0, 0, 1024, 480)
        self.setStyleSheet("background-color: #0a0f1a;")

        # ===== ТЕСТ ЛЕНТЫ =====
        self.rgb = get_rgb()
        if self.rgb.is_available:
            self.rgb.test_mode()
        else:
            print("⚠️ Лента недоступна, пропускаем тест")

        # Крестик
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff3366;
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 18px;
                font-weight: bold;
                padding: 4px 10px;
                min-width: 36px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #ff1744;
            }
        """)
        self.close_btn.setGeometry(self.width() - 50, 8, 40, 40)
        self.close_btn.raise_()
        self.close_btn.clicked.connect(self.close_app)

        # Экраны
        self.demo_screen = DemoScreen()
        self.logs_screen = LogsScreen()
        self.graphs_screen = GraphsScreen()

        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.demo_screen)
        self.stacked.addWidget(self.logs_screen)
        self.stacked.addWidget(self.graphs_screen)

        self.swipe_container = SwipeContainer(self.stacked)
        self.nav = NavigationController(self.swipe_container)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(15)

        btn_demo = QPushButton("🎬 ДЕМО")
        btn_demo.setStyleSheet("background: #1a1f2a; color: #00ffff; border: 1px solid #00ffff; border-radius: 30px; padding: 8px 20px; font-weight: bold; font-size: 12px;")
        btn_demo.clicked.connect(self.nav.go_to_demo)
        btn_layout.addWidget(btn_demo)

        btn_logs = QPushButton("📄 ЛОГИ")
        btn_logs.setStyleSheet("background: #1a1f2a; color: #ff9900; border: 1px solid #ff9900; border-radius: 30px; padding: 8px 20px; font-weight: bold; font-size: 12px;")
        btn_logs.clicked.connect(self.nav.go_to_logs)
        btn_layout.addWidget(btn_logs)

        btn_graphs = QPushButton("📊 ГРАФИКИ")
        btn_graphs.setStyleSheet("background: #1a1f2a; color: #00b4d8; border: 1px solid #00b4d8; border-radius: 30px; padding: 8px 20px; font-weight: bold; font-size: 12px;")
        btn_graphs.clicked.connect(self.nav.go_to_graphs)
        btn_layout.addWidget(btn_graphs)

        btn_theme = QPushButton("🎨 ТЕМА")
        btn_theme.setStyleSheet("background: #1a1f2a; color: #ffcc00; border: 1px solid #ffcc00; border-radius: 30px; padding: 8px 20px; font-weight: bold; font-size: 12px;")
        btn_layout.addWidget(btn_theme)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.addWidget(self.swipe_container, 1)
        main_layout.addLayout(btn_layout)

    def close_app(self):
        """Закрытие через крестик — ВЫКЛЮЧАЕМ ЛЕНТУ"""
        print("✕ Закрытие через крестик...")
        cleanup_rgb()
        self.close()

    def closeEvent(self, event):
        """Переопределяем событие закрытия"""
        print("🛑 Закрытие окна...")
        cleanup_rgb()
        event.accept()

    def resizeEvent(self, event):
        self.close_btn.move(self.width() - 50, 8)
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_D:
            self.nav.go_to_demo()
        elif event.key() == Qt.Key_L:
            self.nav.go_to_logs()
        elif event.key() == Qt.Key_G:
            self.nav.go_to_graphs()
        elif event.key() == Qt.Key_Q or event.key() == Qt.Key_Escape:
            self.close_app()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    try:
        sys.exit(app.exec_())
    finally:
        # Гарантированное выключение при любом завершении
        cleanup_rgb()
        print("👋 Программа завершена")
