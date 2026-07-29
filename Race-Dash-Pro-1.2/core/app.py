#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QIcon

from utils.swipe_container import SwipeContainer
from controllers.navigation import NavigationController
from screens.professional_demo import ProfessionalDemoScreen
from screens.logs_screen import LogsScreen
from screens.graphs_screen import GraphsScreen
from hardware.worker import HardwareThread
from core.config import ConfigManager
from core.state_machine import StateMachine

class RaceDashApp(QWidget):
    """Главное приложение"""
    
    def __init__(self):
        super().__init__()
        
        # --- ЗАГРУЗКА НАСТРОЕК ---
        self.config = ConfigManager()
        self.state_machine = StateMachine()
        
        # --- АППАРАТНЫЙ ПОТОК ---
        self.hardware = HardwareThread()
        self.hardware.data_updated.connect(self.on_data_updated)
        self.hardware.start()
        
        # --- ИНТЕРФЕЙС ---
        self.setup_ui()
        self.apply_theme()
        
        # --- ТАЙМЕРЫ ---
        self._init_timers()
        
        # --- ПЕРЕХОД В СОСТОЯНИЕ IDLE ---
        QTimer.singleShot(2000, lambda: self.state_machine.transition("IDLE"))
    
    def setup_ui(self):
        """Сборка интерфейса"""
        self.setWindowTitle("RACE DASH PRO")
        self.showFullScreen()
        self.setStyleSheet("background-color: #0a0f1a;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- ЭКРАНЫ ---
        self.demo_screen = ProfessionalDemoScreen()
        self.logs_screen = LogsScreen()
        self.graphs_screen = GraphsScreen()
        
        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.demo_screen)
        self.stacked.addWidget(self.logs_screen)
        self.stacked.addWidget(self.graphs_screen)
        
        self.swipe_container = SwipeContainer(self.stacked)
        self.nav = NavigationController(self.swipe_container)
        
        # --- НАВИГАЦИЯ (ИКОНКИ ВМЕСТО ТЕКСТА) ---
        nav_layout = QHBoxLayout()
        nav_layout.setAlignment(Qt.AlignCenter)
        nav_layout.setSpacing(10)
        
        buttons = [
            ("ДЕМО", "images/icons/demo_icon.png", self.nav.go_to_demo),
            ("ЛОГИ", "images/icons/logs_icon.png", self.nav.go_to_logs),
            ("ГРАФИКИ", "images/icons/graphs_icon.png", self.nav.go_to_graphs),
            ("ТЕМА", "images/icons/theme_icon.png", self.toggle_theme),
        ]
        
        for text, icon_path, callback in buttons:
            btn = QPushButton(text)
            if not icon_path:
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(Qt.QSize(24, 24))
            btn.setStyleSheet("""
                QPushButton {
                    background: #1a1f2a;
                    color: #00ffff;
                    border: 1px solid #00ffff;
                    border-radius: 30px;
                    padding: 8px 20px;
                    font-weight: bold;
                    font-size: 12px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background: #00ffff;
                    color: #000;
                }
            """)
            btn.clicked.connect(callback)
            nav_layout.addWidget(btn)
        
        # --- СБОРКА ---
        main_layout.addWidget(self.swipe_container, 1)
        main_layout.addLayout(nav_layout)
        self.setLayout(main_layout)
    
    def apply_theme(self):
        """Применение темы"""
        theme = self.config.get_theme()
        self.setStyleSheet(f"background-color: {theme['bg']};")
    
    def toggle_theme(self):
        """Переключение темы"""
        self.config.next_theme()
        self.apply_theme()
    
    def _init_timers(self):
        """Инициализация таймеров"""
        self._fps_timer = QTimer()
        self._fps_timer.timeout.connect(self.update_ui)
        self._fps_timer.start(50)  # 20 FPS
    
    @pyqtSlot(dict)
    def on_data_updated(self, data):
        """Обновление данных с железа"""
        if self.stacked.currentWidget() == self.demo_screen:
            self.demo_screen.update_data(data)
    
    def update_ui(self):
        """Обновление UI (если нужно)"""
        pass
    
    def closeEvent(self, event):
        """Закрытие приложения"""
        print("🛑 Завершение работы...")
        self.hardware.stop()
        event.accept()