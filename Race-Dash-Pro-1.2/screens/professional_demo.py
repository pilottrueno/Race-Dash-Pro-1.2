#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Профессиональный экран приборной панели в стиле Haltek/AEM
Стекло над углепластиком - Dark Carbon Fiber
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter

from widgets.professional_gauge import ProfessionalGauge

class ProfessionalDemoScreen(QWidget):
    """Экран с профессиональным прибором"""
    
    # Сигнал для навигации (если нужно)
    navigate_to = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- ОСНОВНОЙ LAYOUT ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- ПРОФЕССИОНАЛЬНЫЙ ПРИБОР ---
        self.gauge = ProfessionalGauge()
        layout.addWidget(self.gauge)
        
        # --- ВЕРХНИЙ СЛОЙ (поверх прибора) ---
        self._setup_overlay()
        
        # --- АНИМАЦИЯ ПРИ ПОЯВЛЕНИИ ---
        self.setWindowOpacity(0.0)
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self._fade_in)
        self.fade_timer.start(20)
        self._fade_opacity = 0.0
        
        # --- ТАЙМЕР ДЛЯ ДЕМО-ДАННЫХ (если нет реальных) ---
        self._demo_mode = True
        self._demo_timer = QTimer()
        self._demo_timer.timeout.connect(self._generate_demo_data)
        self._demo_timer.start(50)  # 20 Гц
        
        # --- КЛАВИШИ УПРАВЛЕНИЯ (поверх, но прозрачные) ---
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_KeyCompression)
    
    def _setup_overlay(self):
        """Настройка наложенных элементов управления"""
        # Будет реализовано позже для кнопок поверх приборов
        pass
    
    def _fade_in(self):
        """Плавное появление экрана"""
        self._fade_opacity += 0.05
        if self._fade_opacity >= 1.0:
            self._fade_opacity = 1.0
            self.fade_timer.stop()
        self.setWindowOpacity(self._fade_opacity)
    
    def _generate_demo_data(self):
        """Генерация демо-данных"""
        if not self._demo_mode:
            return
        
        import time
        t = time.time() % 10
        
        if t < 3:
            rpm = 800 + t * 2400
        elif t < 6:
            rpm = 8000
        else:
            rpm = 8000 - (t - 6) * 2400
        
        rpm = int(max(800, min(8000, rpm)))
        load = rpm / 8000
        
        # Передача
        if rpm < 1500:
            gear = 0
        elif rpm < 3000:
            gear = 1
        elif rpm < 4500:
            gear = 2
        elif rpm < 6000:
            gear = 3
        else:
            gear = 4
        
        data = {
            'rpm': rpm,
            'speed': int(rpm / 30),
            'gear': gear,
            'coolant': int(85 + load * 40),
            'oil_temp': int(90 + load * 50),
            'oil_press': round(1.2 + load * 4.3, 1),
            'boost': round(load * 1.5, 2),
            'lap_time': t,
            'voltage': round(14.2 - load * 0.8, 1),
            'egt': int(400 + load * 600),
            'lambda': round(1.0 - load * 0.12, 2),
            'afr': round((1.0 - load * 0.12) * 14.7, 1),
            'fuel_press': round(3.8 + load * 1.5, 1),
            'intake': int(20 + load * 30),
            'fuel_temp': int(30 + load * 25),
            'ambient': int(20 + load * 15),
            'tps': int(load * 100)
        }
        
        self.update_data(data)
    
    def update_data(self, data):
        """Обновление данных с оборудования"""
        self.gauge.update_data(data)
    
    def keyPressEvent(self, event):
        """Обработка клавиш"""
        if event.key() == Qt.Key_D:
            # Переключение демо-режима
            self._demo_mode = not self._demo_mode
            print(f"Демо-режим: {'ВКЛ' if self._demo_mode else 'ВЫКЛ'}")
        elif event.key() == Qt.Key_R:
            # Сброс пика
            self.gauge.reset_peak()
        elif event.key() == Qt.Key_F:
            # Переключение полноэкранного режима
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_Escape:
            # Выход
            self.close()
        else:
            super().keyPressEvent(event)
    
    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def set_recording(self, recording):
        """Установка статуса записи"""
        self.gauge.set_recording(recording)
    
    def set_rpm_limits(self, max_rpm=8000, redline=7000):
        """Установка лимитов RPM"""
        self.gauge.set_rpm_limits(max_rpm, redline)
    
    def set_gear(self, gear):
        """Установка передачи"""
        self.gauge.set_gear(gear)
    
    def set_lap_time(self, seconds):
        """Установка времени круга"""
        self.gauge.set_lap_time(seconds)
    
    def enterEvent(self, event):
        """При входе в виджет"""
        self.setFocus()
        super().enterEvent(event)
    
    def resizeEvent(self, event):
        """При изменении размера"""
        super().resizeEvent(event)
        # Здесь можно обновить пропорции элементов