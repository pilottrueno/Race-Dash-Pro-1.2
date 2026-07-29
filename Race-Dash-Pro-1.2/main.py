#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RACE DASH PRO v1.2
Professional Motorsport Dashboard
"""

import sys
import signal
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer
from core.app import RaceDashApp  # <-- Вся логика в core/app.py

def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальный обработчик исключений"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА:\n{exc_value}", file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def signal_handler(sig, frame):
    """Обработчик сигналов (Ctrl+C)"""
    print("\n🛑 Получен сигнал завершения...")
    QApplication.quit()

if __name__ == '__main__':
    # --- ИНИЦИАЛИЗАЦИЯ ---
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("RACE DASH PRO")
    app.setApplicationVersion("1.2")
    app.setWindowIcon(QIcon("images/icons/rdp_icon.png"))
    
    # --- ЗАСТАВКА ---
    splash_pixmap = QPixmap("images/splash/splash.png")
    splash = None
    if not splash_pixmap.isNull():
        splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
    
    # --- ОБРАБОТЧИКИ ---
    sys.excepthook = handle_exception
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # --- ЗАПУСК ПРИЛОЖЕНИЯ ---
    try:
        window = RaceDashApp()  # <-- Класс из core/app.py
        if splash:
            splash.finish(window)
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)
