#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Профессиональный гоночный прибор в стиле Haltek/AEM
Стекло над углепластиком - Dark Carbon Fiber
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, QTimer
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush, QFont, QLinearGradient, QConicalGradient, QRadialGradient
import time
import math

class ProfessionalGauge(QWidget):
    """Гоночный прибор в стиле Haltek/AEM"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- ДАННЫЕ ---
        self._rpm = 0
        self._speed = 0
        self._gear = 0
        self._coolant = 70
        self._oil_temp = 80
        self._oil_press = 4.2
        self._boost = 0.0
        self._lap_time = 0
        self._recording = False
        self._rpm_max = 8000
        self._rpm_redline = 7000
        
        # Целевые значения для анимации
        self._target_rpm = 0
        self._target_speed = 0
        
        # Анимации
        self.rpm_anim = QPropertyAnimation(self, b'rpm')
        self.rpm_anim.setDuration(150)
        self.rpm_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.speed_anim = QPropertyAnimation(self, b'speed')
        self.speed_anim.setDuration(150)
        self.speed_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Таймер для пульсации красной зоны
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.update)
        self.pulse_timer.start(100)
        self._pulse_state = False
        
        # Шрифты
        self.font_digital = QFont("DS-Digital, Share Tech Mono, monospace")
        self.font_digital.setBold(True)
        
        self.font_mono = QFont("Roboto Mono, monospace")
        self.font_mono.setBold(True)
        
        # Устанавливаем минимальный размер
        self.setMinimumSize(600, 400)
        
        # Настройки цвета
        self.bg_color = QColor(10, 15, 26)
        self.card_bg = QColor(20, 25, 35)
        self.accent = QColor(0, 255, 204)
        self.red = QColor(255, 51, 102)
        self.orange = QColor(255, 153, 0)
        self.green = QColor(76, 175, 80)
        self.white = QColor(255, 255, 255)
        self.gray = QColor(100, 100, 100)
        self.dark_gray = QColor(40, 45, 55)
        self.carbon = QColor(30, 35, 45)
    
    # ==================== СВОЙСТВА ДЛЯ АНИМАЦИИ ====================
    
    @pyqtProperty(float)
    def rpm(self):
        return self._rpm
    
    @rpm.setter
    def rpm(self, value):
        if value != self._rpm:
            self._rpm = value
            self.update()
    
    @pyqtProperty(float)
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, value):
        if value != self._speed:
            self._speed = value
            self.update()
    
    def set_rpm_animated(self, value):
        self._target_rpm = value
        self.rpm_anim.setStartValue(self._rpm)
        self.rpm_anim.setEndValue(value)
        self.rpm_anim.start()
    
    def set_speed_animated(self, value):
        self._target_speed = value
        self.speed_anim.setStartValue(self._speed)
        self.speed_anim.setEndValue(value)
        self.speed_anim.start()
    
    def update_data(self, data):
        """Обновление всех данных"""
        if 'rpm' in data:
            self.set_rpm_animated(data['rpm'])
        if 'speed' in data:
            self.set_speed_animated(data['speed'])
        if 'gear' in data:
            self._gear = data['gear']
        if 'coolant' in data:
            self._coolant = data['coolant']
        if 'oil_temp' in data:
            self._oil_temp = data['oil_temp']
        if 'oil_press' in data:
            self._oil_press = data['oil_press']
        if 'boost' in data:
            self._boost = data['boost']
        if 'lap_time' in data:
            self._lap_time = data['lap_time']
        if 'recording' in data:
            self._recording = data['recording']
        self.update()
    
    # ==================== ОСНОВНАЯ ОТРИСОВКА ====================
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        w = self.width()
        h = self.height()
        
        # --- ФОН (карбон) ---
        self._draw_carbon_background(painter, w, h)
        
        # --- ВЕРХНЯЯ СТРОКА СТАТУСА ---
        self._draw_status_bar(painter, w, h)
        
        # --- RPM ДУГА (левый фланг) ---
        self._draw_rpm_arc(painter, w, h)
        
        # --- ЦЕНТР (Скорость + Передача) ---
        self._draw_speed_center(painter, w, h)
        
        # --- ПРАВЫЙ ФЛАНГ (Температуры) ---
        self._draw_temp_bars(painter, w, h)
        
        # --- BOOST (над правым флангом) ---
        self._draw_boost(painter, w, h)
        
        # --- НИЖНЯЯ ПАНЕЛЬ НАВИГАЦИИ ---
        self._draw_nav_bar(painter, w, h)
        
        # --- УГЛЕПЛАСТИКОВЫЙ ЭФФЕКТ (поверх) ---
        self._draw_carbon_effect(painter, w, h)
    
    # ==================== КАРБОНОВЫЙ ФОН ====================
    
    def _draw_carbon_background(self, painter, w, h):
        """Карбоновый фон с текстурой"""
        # Основной фон
        painter.fillRect(0, 0, w, h, self.bg_color)
        
        # Имитация карбоновой текстуры (линии)
        painter.setPen(QPen(self.carbon, 1))
        for i in range(0, w, 8):
            painter.drawLine(i, 0, i + 4, h)
        for i in range(0, h, 8):
            painter.drawLine(0, i, w, i + 4)
        
        # Градиентная затемнённая область по краям
        gradient = QRadialGradient(w/2, h/2, min(w, h))
        gradient.setColorAt(0.3, QColor(0, 0, 0, 0))
        gradient.setColorAt(1, QColor(0, 0, 0, 80))
        painter.fillRect(0, 0, w, h, gradient)
    
    def _draw_carbon_effect(self, painter, w, h):
        """Эффект стекла поверх панели (блик)"""
        # Глянцевый блик сверху
        gradient = QLinearGradient(0, 0, 0, h * 0.3)
        gradient.setColorAt(0, QColor(255, 255, 255, 8))
        gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillRect(0, 0, w, h * 0.3, gradient)
    
    # ==================== ВЕРХНЯЯ СТРОКА ====================
    
    def _draw_status_bar(self, painter, w, h):
        """Верхняя строка статуса"""
        bar_y = 15
        bar_h = 30
        
        # Полоса
        painter.setPen(QPen(self.dark_gray, 1))
        painter.drawLine(20, bar_y + bar_h, w - 20, bar_y + bar_h)
        
        # REC индикатор
        if self._recording:
            painter.setBrush(self.red)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(25, bar_y + 8, 8, 8)
            
            painter.setPen(self.white)
            painter.setFont(self.font_mono)
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            painter.drawText(38, bar_y + 16, "REC")
        
        # Напряжение
        painter.setPen(self.gray)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(w - 230, bar_y + 16, "⚡ 13.8V")
        
        # Температура масла
        painter.drawText(w - 165, bar_y + 16, f"🛢️ {int(self._oil_temp)}°C")
        
        # Таймер сессии
        painter.setPen(self.accent)
        minutes = int(self._lap_time // 60)
        seconds = int(self._lap_time % 60)
        centiseconds = int((self._lap_time % 1) * 100)
        painter.drawText(w - 90, bar_y + 16, f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}")
    
    # ==================== RPM ДУГА ====================
    
    def _draw_rpm_arc(self, painter, w, h):
        """Дуга тахометра (левый фланг)"""
        cx = w * 0.28
        cy = h * 0.52
        radius = min(w * 0.22, h * 0.38)
        
        # Углы
        start_angle = -135
        end_angle = 135
        span = end_angle - start_angle
        
        # --- Фон дуги ---
        painter.setPen(QPen(self.dark_gray, 20))
        painter.drawArc(
            int(cx - radius), int(cy - radius), 
            int(radius * 2), int(radius * 2),
            start_angle * 16, span * 16
        )
        
        # --- Активная дуга (с градиентом) ---
        rpm_pct = min(max(self._rpm / self._rpm_max, 0), 1.0)
        active_angle = start_angle + rpm_pct * span
        
        # Градиент для дуги (от циана к красному)
        gradient = QConicalGradient(cx, cy, start_angle)
        
        # Цвета для разных зон
        if rpm_pct < 0.3:
            gradient.setColorAt(0, QColor(0, 200, 255))
            gradient.setColorAt(1, QColor(0, 255, 204))
        elif rpm_pct < 0.6:
            gradient.setColorAt(0, QColor(0, 255, 204))
            gradient.setColorAt(0.7, QColor(255, 204, 0))
            gradient.setColorAt(1, QColor(255, 153, 0))
        else:
            gradient.setColorAt(0, QColor(0, 255, 204))
            gradient.setColorAt(0.4, QColor(255, 204, 0))
            gradient.setColorAt(0.7, QColor(255, 153, 0))
            gradient.setColorAt(1, QColor(255, 51, 102))
        
        painter.setPen(QPen(gradient, 20))
        painter.drawArc(
            int(cx - radius), int(cy - radius), 
            int(radius * 2), int(radius * 2),
            start_angle * 16, int(active_angle * 16)
        )
        
        # --- КРАСНАЯ ЗОНА (пульсация) ---
        if rpm_pct > 0.85:
            self._pulse_state = not self._pulse_state
            if self._pulse_state:
                painter.setPen(QPen(self.red, 20))
                red_start = start_angle + 0.85 * span
                painter.drawArc(
                    int(cx - radius), int(cy - radius), 
                    int(radius * 2), int(radius * 2),
                    int(red_start * 16), int((active_angle - red_start) * 16)
                )
        
        # --- МЕТКИ НА ДУГЕ ---
        painter.setPen(self.gray)
        font = painter.font()
        font.setPointSize(int(radius * 0.08))
        painter.setFont(font)
        
        for i in range(9):
            angle = start_angle + i * (span / 8)
            val = int(i * 1000)
            if val > 0:
                rad = math.radians(angle)
                # Координаты меток (снаружи дуги)
                label_radius = radius + 25
                x = cx + label_radius * math.cos(rad)
                y = cy + label_radius * math.sin(rad)
                # Корректировка позиции текста
                fm = painter.fontMetrics()
                text = f"{val}"
                painter.drawText(int(x - fm.width(text)/2), int(y + fm.height()/3), text)
        
        # --- ЦИФРЫ RPM ---
        painter.setPen(self.white)
        font = painter.font()
        font.setPointSize(int(radius * 0.45))
        font.setBold(True)
        painter.setFont(font)
        
        rpm_text = f"{int(self._rpm)}"
        fm = painter.fontMetrics()
        painter.drawText(
            int(cx - fm.width(rpm_text) / 2), 
            int(cy + radius * 0.45), 
            rpm_text
        )
        
        # Подпись RPM
        painter.setPen(self.gray)
        font.setPointSize(int(radius * 0.1))
        painter.setFont(font)
        painter.drawText(
            int(cx - 20), 
            int(cy + radius * 0.58), 
            "RPM"
        )
    
    # ==================== ЦЕНТРАЛЬНЫЙ СПИДОМЕТР ====================
    
    def _draw_speed_center(self, painter, w, h):
        """Центральный спидометр"""
        cx = w * 0.52
        cy = h * 0.45
        
        # --- КРУГЛЫЙ ФОН ---
        radius = min(w * 0.15, h * 0.25)
        
        # Тень
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - radius - 5), int(cy - radius - 5), 
                           int(radius * 2 + 10), int(radius * 2 + 10))
        
        # Основной круг
        painter.setBrush(self.card_bg)
        painter.setPen(QPen(self.dark_gray, 2))
        painter.drawEllipse(int(cx - radius), int(cy - radius), 
                           int(radius * 2), int(radius * 2))
        
        # Внутренняя подсветка
        grad = QRadialGradient(cx, cy, radius)
        grad.setColorAt(0, QColor(0, 255, 204, 20))
        grad.setColorAt(1, QColor(0, 255, 204, 0))
        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - radius), int(cy - radius), 
                           int(radius * 2), int(radius * 2))
        
        # --- ЦИФРЫ СКОРОСТИ ---
        painter.setPen(self.white)
        font = painter.font()
        font.setPointSize(int(radius * 0.7))
        font.setBold(True)
        painter.setFont(font)
        
        speed_text = f"{int(self._speed)}"
        fm = painter.fontMetrics()
        painter.drawText(
            int(cx - fm.width(speed_text) / 2), 
            int(cy + radius * 0.2), 
            speed_text
        )
        
        # Единицы измерения
        painter.setPen(self.gray)
        font.setPointSize(int(radius * 0.15))
        painter.setFont(font)
        painter.drawText(
            int(cx - 25), 
            int(cy + radius * 0.45), 
            "km/h"
        )
        
        # --- ПЕРЕДАЧА ---
        painter.setPen(self.accent)
        font.setPointSize(int(radius * 0.25))
        font.setBold(True)
        painter.setFont(font)
        
        gear_text = self._get_gear_text()
        fm = painter.fontMetrics()
        painter.drawText(
            int(cx - fm.width(gear_text) / 2), 
            int(cy + radius * 0.75), 
            gear_text
        )
    
    def _get_gear_text(self):
        """Текст передачи"""
        if self._gear == 0:
            return "[N]"
        elif self._gear == -1:
            return "[R]"
        elif self._gear == 1:
            return "1st"
        elif self._gear == 2:
            return "2nd"
        elif self._gear == 3:
            return "3rd"
        else:
            return f"{self._gear}th"
    
    # ==================== ТЕРМОМЕТРЫ ====================
    
    def _draw_temp_bars(self, painter, w, h):
        """Вертикальные термометры (правый фланг)"""
        bar_x = w * 0.82
        bar_width = 22
        bar_height = h * 0.45
        bar_spacing = 12
        start_y = (h - bar_height) / 2 - 20
        
        # Температура ОЖ
        self._draw_vertical_bar(
            painter, bar_x, start_y, bar_width, bar_height,
            self._coolant, 50, 130,
            QColor(0, 100, 255), QColor(255, 204, 0), QColor(255, 51, 102),
            "Coolant", "°C"
        )
        
        # Температура масла
        self._draw_vertical_bar(
            painter, bar_x + bar_width + bar_spacing, start_y, bar_width, bar_height,
            self._oil_temp, 60, 150,
            QColor(0, 200, 100), QColor(255, 204, 0), QColor(255, 51, 102),
            "Oil", "°C"
        )
        
        # Давление масла
        self._draw_vertical_bar(
            painter, bar_x + (bar_width + bar_spacing) * 2, start_y, bar_width, bar_height,
            self._oil_press, 1, 6,
            QColor(0, 200, 255), QColor(255, 204, 0), QColor(255, 51, 102),
            "Pressure", "bar"
        )
    
    def _draw_vertical_bar(self, painter, x, y, w, h, value, min_val, max_val,
                          color1, color2, color3, label, unit):
        """Отрисовка вертикального термометра"""
        # --- ФОН ---
        painter.setPen(QPen(self.dark_gray, 1))
        painter.setBrush(QBrush(self.card_bg))
        painter.drawRoundedRect(int(x), int(y), int(w), int(h), 4, 4)
        
        # --- ЗАПОЛНЕНИЕ ---
        pct = max(0, min(1, (value - min_val) / (max_val - min_val)))
        fill_h = int(h * pct)
        
        if fill_h > 0:
            # Градиент заполнения
            gradient = QLinearGradient(x, y + h, x, y)
            if pct < 0.5:
                gradient.setColorAt(0, color1)
                gradient.setColorAt(1, color1.lighter(150))
            elif pct < 0.75:
                gradient.setColorAt(0, color2)
                gradient.setColorAt(1, color2.lighter(150))
            else:
                gradient.setColorAt(0, color3)
                gradient.setColorAt(1, color3.lighter(150))
            
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(
                int(x + 2), int(y + h - fill_h), 
                int(w - 4), int(fill_h - 2), 
                2, 2
            )
        
        # --- ЗНАЧЕНИЕ ---
        painter.setPen(self.white)
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        val_text = f"{value:.1f}"
        fm = painter.fontMetrics()
        painter.drawText(
            int(x + w/2 - fm.width(val_text)/2), 
            int(y + h + 18), 
            val_text
        )
        
        # --- МЕТКА ---
        painter.setPen(self.gray)
        font.setPointSize(7)
        painter.setFont(font)
        painter.drawText(
            int(x + w/2 - 18), 
            int(y - 8), 
            label
        )
    
    # ==================== BOOST ====================
    
    def _draw_boost(self, painter, w, h):
        """Индикатор наддува (над правым флангом)"""
        x = w * 0.82
        y = h * 0.10
        width = w * 0.15
        height = 35
        
        # Фон
        painter.setPen(QPen(self.dark_gray, 1))
        painter.setBrush(QBrush(self.card_bg))
        painter.drawRoundedRect(int(x), int(y), int(width), int(height), 6, 6)
        
        # Заполнение
        boost_pct = min(max(self._boost / 2.5, 0), 1)
        fill_w = int((width - 6) * boost_pct)
        
        if fill_w > 0:
            gradient = QLinearGradient(x, y, x + width, y)
            if boost_pct < 0.5:
                gradient.setColorAt(0, QColor(0, 200, 255))
                gradient.setColorAt(1, QColor(0, 255, 204))
            elif boost_pct < 0.8:
                gradient.setColorAt(0, QColor(0, 255, 204))
                gradient.setColorAt(1, QColor(255, 204, 0))
            else:
                gradient.setColorAt(0, QColor(255, 204, 0))
                gradient.setColorAt(1, QColor(255, 51, 102))
            
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(
                int(x + 3), int(y + 3), 
                fill_w, int(height - 6), 
                4, 4
            )
        
        # Текст
        painter.setPen(self.white)
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        boost_text = f"{self._boost:.1f} bar"
        fm = painter.fontMetrics()
        painter.drawText(
            int(x + width/2 - fm.width(boost_text)/2), 
            int(y + height/2 + 4), 
            boost_text
        )
        
        # Метка
        painter.setPen(self.gray)
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(int(x + width/2 - 14), int(y - 6), "BOOST")
    
    # ==================== НИЖНЯЯ ПАНЕЛЬ НАВИГАЦИИ ====================
    
    def _draw_nav_bar(self, painter, w, h):
        """Нижняя панель навигации (профессиональный стиль)"""
        bar_y = h - 45
        bar_h = 45
        
        # Фон
        painter.fillRect(0, bar_y, w, bar_h, QColor(15, 20, 30, 200))
        painter.setPen(QPen(QColor(30, 35, 45), 1))
        painter.drawLine(0, bar_y, w, bar_y)
        
        # Иконки навигации (в стиле Haltek)
        icons = [
            ("⏱️", True),    # Демо / Основной экран
            ("📊", False),   # Графики
            ("📄", False),   # Логи
            ("⚙️", False),   # Настройки
        ]
        
        icon_width = w / len(icons)
        for i, (icon, active) in enumerate(icons):
            x = i * icon_width + icon_width / 2
            
            # Индикатор активности (подсветка снизу)
            if active:
                painter.setPen(QPen(self.accent, 2))
                painter.drawLine(int(x - 15), int(bar_y + bar_h - 4), int(x + 15), int(bar_y + bar_h - 4))
            
            # Иконка
            painter.setPen(self.accent if active else self.gray)
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)
            painter.drawText(int(x - 15), int(bar_y + 32), icon)
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def set_recording(self, recording):
        """Установка статуса записи"""
        self._recording = recording
        self.update()
    
    def set_rpm_limits(self, max_rpm, redline):
        """Установка лимитов RPM"""
        self._rpm_max = max_rpm
        self._rpm_redline = redline
    
    def set_gear(self, gear):
        """Установка передачи"""
        self._gear = gear
        self.update()
    
    def set_lap_time(self, seconds):
        """Установка времени круга"""
        self._lap_time = seconds
        self.update()