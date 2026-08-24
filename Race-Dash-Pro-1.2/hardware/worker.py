#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hardware Worker — Асинхронный опрос оборудования
Работает в отдельном потоке, не блокирует GUI
"""

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
import time
import math
from typing import Dict, Any, Optional
from enum import Enum

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ============================================

class SensorStatus(Enum):
    """Статус датчика"""
    OK = 0
    WARNING = 1
    ERROR = 2
    DISCONNECTED = 3

class SensorData:
    """Данные с датчика с типом и статусом"""
    def __init__(self, value: Optional[float] = None, status: SensorStatus = SensorStatus.ERROR):
        self.value = value
        self.status = status
        self.timestamp = time.time()
    
    def is_valid(self) -> bool:
        return self.status == SensorStatus.OK and self.value is not None

# ============================================
# ОСНОВНОЙ КЛАСС
# ============================================

class HardwareWorker(QObject):
    """
    Асинхронный опрос оборудования в отдельном потоке
    Эмулирует работу с CAN, GPS, датчиками
    """
    
    # Сигналы для передачи данных в GUI
    data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    connection_status = pyqtSignal(bool)
    
    def __init__(self, demo_mode: bool = True):
        """
        Инициализация HardwareWorker
        
        Args:
            demo_mode: True — эмуляция данных, False — чтение с реального оборудования
        """
        super().__init__()
        self.running = True
        self.demo_mode = demo_mode
        
        # Хранилище данных с датчиков
        self.data = {
            'rpm': SensorData(0, SensorStatus.DISCONNECTED),
            'speed': SensorData(0, SensorStatus.DISCONNECTED),
            'gear': SensorData(0, SensorStatus.DISCONNECTED),
            'boost': SensorData(0, SensorStatus.DISCONNECTED),
            'coolant': SensorData(0, SensorStatus.DISCONNECTED),
            'oil_temp': SensorData(0, SensorStatus.DISCONNECTED),
            'oil_press': SensorData(0, SensorStatus.DISCONNECTED),
            'voltage': SensorData(0, SensorStatus.DISCONNECTED),
            'egt': SensorData(0, SensorStatus.DISCONNECTED),
            'lambda': SensorData(0, SensorStatus.DISCONNECTED),
            'afr': SensorData(0, SensorStatus.DISCONNECTED),
            'fuel_press': SensorData(0, SensorStatus.DISCONNECTED),
            'intake': SensorData(0, SensorStatus.DISCONNECTED),
            'fuel_temp': SensorData(0, SensorStatus.DISCONNECTED),
            'ambient': SensorData(0, SensorStatus.DISCONNECTED),
            'tps': SensorData(0, SensorStatus.DISCONNECTED),
            'lap_time': SensorData(0, SensorStatus.DISCONNECTED),
            'gps_lat': SensorData(0, SensorStatus.DISCONNECTED),
            'gps_lon': SensorData(0, SensorStatus.DISCONNECTED),
            'gps_speed': SensorData(0, SensorStatus.DISCONNECTED),
            'gps_satellites': SensorData(0, SensorStatus.DISCONNECTED),
            'gps_fix': SensorData(False, SensorStatus.DISCONNECTED),
            'recording': SensorData(False, SensorStatus.OK),
        }
        
        # Для демо-режима
        self._demo_time = 0
        self._last_rpm = 0
        self._gear = 0
        
        # Для реального режима (заглушка)
        self._can_available = False
        self._gps_available = False
        
        # Инициализация оборудования
        self._init_hardware()
    
    # ============================================
    # ИНИЦИАЛИЗАЦИЯ ОБОРУДОВАНИЯ
    # ============================================
    
    def _init_hardware(self):
        """Инициализация реального оборудования (если не в демо-режиме)"""
        if self.demo_mode:
            print("🔄 Hardware: Демо-режим (эмуляция данных)")
            self.connection_status.emit(True)
            return
        
        print("🔧 Hardware: Инициализация оборудования...")
        
        # Попытка подключения к CAN-шине
        try:
            self._init_can()
        except Exception as e:
            print(f"⚠️ CAN не инициализирован: {e}")
        
        # Попытка подключения к GPS
        try:
            self._init_gps()
        except Exception as e:
            print(f"⚠️ GPS не инициализирован: {e}")
    
    def _init_can(self):
        """Инициализация CAN-шины"""
        try:
            import can
            # Настройка для реальной CAN шины
            # self._can_bus = can.interface.Bus(channel='can0', bustype='socketcan')
            self._can_available = True
            print("   ✅ CAN шина доступна")
        except ImportError:
            print("   ⚠️ Библиотека python-can не установлена")
        except Exception as e:
            print(f"   ⚠️ Ошибка CAN: {e}")
    
    def _init_gps(self):
        """Инициализация GPS-модуля"""
        try:
            import serial
            import pynmea2
            # self._gps_serial = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
            self._gps_available = True
            print("   ✅ GPS модуль доступен")
        except ImportError:
            print("   ⚠️ Библиотека pynmea2 или pyserial не установлена")
        except Exception as e:
            print(f"   ⚠️ Ошибка GPS: {e}")
    
    # ============================================
    # УПРАВЛЕНИЕ ПОТОКОМ
    # ============================================
    
    def start(self):
        """Запуск опроса оборудования"""
        self.running = True
        self._update_loop()
    
    def stop(self):
        """Остановка опроса"""
        self.running = False
    
    def _update_loop(self):
        """Цикл обновления данных (вызывается рекурсивно)"""
        if not self.running:
            return
        
        try:
            if self.demo_mode:
                self._update_demo()
            else:
                self._update_real()
            
            self.data_updated.emit(self._get_data_dict())
            
        except Exception as e:
            self.error_occurred.emit(str(e))
        
        # Планируем следующее обновление через 50 мс (20 Гц)
        QTimer.singleShot(50, self._update_loop)
    
    # ============================================
    # ОБНОВЛЕНИЕ ДАННЫХ (ДЕМО)
    # ============================================
    
    def _update_demo(self):
        """Обновление демо-данных (эмуляция работы двигателя)"""
        self._demo_time += 0.05
        
        # Цикл 10 секунд
        if self._demo_time > 10:
            self._demo_time = 0
        
        # Профиль RPM: разгон → пик → сброс
        if self._demo_time < 3:
            rpm = 800 + self._demo_time * 2400
        elif self._demo_time < 6:
            rpm = 8000
        elif self._demo_time < 8:
            rpm = 8000 - (self._demo_time - 6) * 3000
        else:
            rpm = 2000
        
        rpm = int(max(800, min(8000, rpm)))
        load = rpm / 8000
        
        # Скорость (зависит от RPM)
        speed = int(rpm / 35)
        
        # Передача
        if speed < 10:
            gear = 0
        elif speed < 30:
            gear = 1
        elif speed < 50:
            gear = 2
        elif speed < 80:
            gear = 3
        elif speed < 120:
            gear = 4
        else:
            gear = 5
        
        # Остальные параметры
        boost = round(load * 2.0, 2)
        coolant = int(85 + load * 35)
        oil_temp = int(90 + load * 40)
        oil_press = round(1.2 + load * 4.0, 1)
        voltage = round(14.2 - load * 0.6, 1)
        egt = int(400 + load * 500)
        lambda_val = round(1.0 - load * 0.1, 3)
        afr = round(lambda_val * 14.7, 1)
        fuel_press = round(3.8 + load * 1.2, 1)
        intake = int(20 + load * 25)
        fuel_temp = int(30 + load * 20)
        ambient = int(20 + load * 10)
        tps = int(load * 100)
        
        # Запись логов
        recording = rpm > 1000
        
        # Обновляем данные
        self.data['rpm'] = SensorData(rpm, SensorStatus.OK)
        self.data['speed'] = SensorData(speed, SensorStatus.OK)
        self.data['gear'] = SensorData(gear, SensorStatus.OK)
        self.data['boost'] = SensorData(boost, SensorStatus.OK)
        self.data['coolant'] = SensorData(coolant, SensorStatus.OK)
        self.data['oil_temp'] = SensorData(oil_temp, SensorStatus.OK)
        self.data['oil_press'] = SensorData(oil_press, SensorStatus.OK)
        self.data['voltage'] = SensorData(voltage, SensorStatus.OK)
        self.data['egt'] = SensorData(egt, SensorStatus.OK)
        self.data['lambda'] = SensorData(lambda_val, SensorStatus.OK)
        self.data['afr'] = SensorData(afr, SensorStatus.OK)
        self.data['fuel_press'] = SensorData(fuel_press, SensorStatus.OK)
        self.data['intake'] = SensorData(intake, SensorStatus.OK)
        self.data['fuel_temp'] = SensorData(fuel_temp, SensorStatus.OK)
        self.data['ambient'] = SensorData(ambient, SensorStatus.OK)
        self.data['tps'] = SensorData(tps, SensorStatus.OK)
        self.data['lap_time'] = SensorData(self._demo_time, SensorStatus.OK)
        self.data['gps_speed'] = SensorData(speed * 1.2, SensorStatus.OK)
        self.data['gps_fix'] = SensorData(True, SensorStatus.OK)
        self.data['recording'] = SensorData(recording, SensorStatus.OK)
        
        # Эмуляция GPS координат (движение по кругу)
        lat = 55.7558 + math.sin(self._demo_time * 0.3) * 0.01
        lon = 37.6173 + math.cos(self._demo_time * 0.3) * 0.01
        self.data['gps_lat'] = SensorData(lat, SensorStatus.OK)
        self.data['gps_lon'] = SensorData(lon, SensorStatus.OK)
        self.data['gps_satellites'] = SensorData(10, SensorStatus.OK)
        
        self.connection_status.emit(True)
    
    # ============================================
    # ОБНОВЛЕНИЕ ДАННЫХ (РЕАЛЬНОЕ ЖЕЛЕЗО)
    # ============================================
    
    def _update_real(self):
        """
        Обновление данных с реального оборудования
        Здесь будет код для чтения с CAN, GPS, датчиков
        """
        # ===== CAN шина =====
        if self._can_available:
            try:
                # Чтение данных с CAN
                # rpm = self._read_can_rpm()
                # coolant = self._read_can_coolant()
                # ...
                pass
            except Exception as e:
                self.error_occurred.emit(f"CAN ошибка: {e}")
        
        # ===== GPS =====
        if self._gps_available:
            try:
                # Чтение данных с GPS
                # lat, lon, speed = self._read_gps()
                # ...
                pass
            except Exception as e:
                self.error_occurred.emit(f"GPS ошибка: {e}")
        
        # ===== Датчики (аналоговые) =====
        # Здесь чтение с ADC, термопар и т.д.
    
    # ============================================
    # ПРЕОБРАЗОВАНИЕ ДАННЫХ ДЛЯ GUI
    # ============================================
    
    def _get_data_dict(self) -> Dict[str, Any]:
        """
        Преобразование внутреннего формата в словарь для GUI
        
        Returns:
            Словарь с данными для виджетов
        """
        result = {}
        for key, sensor in self.data.items():
            # Основное значение
            result[key] = sensor.value if sensor.is_valid() else 0
            
            # Статус (для отладки)
            result[f'{key}_status'] = sensor.status.name
        
        # Добавляем дополнительные поля
        result['is_demo'] = self.demo_mode
        
        return result
    
    # ============================================
    # МЕТОДЫ ДЛЯ УПРАВЛЕНИЯ
    # ============================================
    
    def set_demo_mode(self, enabled: bool):
        """Включение/отключение демо-режима"""
        self.demo_mode = enabled
        if enabled:
            print("🔄 Демо-режим включён")
        else:
            print("🔧 Демо-режим выключен, переход на реальное оборудование")
    
    def set_recording(self, enabled: bool):
        """Включение/отключение записи логов"""
        self.data['recording'] = SensorData(enabled, SensorStatus.OK)
        print(f"📝 Запись логов: {'ВКЛ' if enabled else 'ВЫКЛ'}")
    
    def reset_peak(self):
        """Сброс пиковых значений"""
        # Можно добавить логику сброса пиков
        print("🏁 Сброс пиковых значений")
    
    def get_last_data(self) -> Dict[str, Any]:
        """Получить последние данные без ожидания"""
        return self._get_data_dict()

# ============================================
# ПОТОК ДЛЯ ХАРДВЕРА
# ============================================

class HardwareThread(QThread):
    """
    Поток для асинхронной работы с оборудованием
    """
    
    data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    connection_status = pyqtSignal(bool)
    
    def __init__(self, demo_mode: bool = True):
        super().__init__()
        self.worker = HardwareWorker(demo_mode)
        self.worker.data_updated.connect(self.data_updated)
        self.worker.error_occurred.connect(self.error_occurred)
        self.worker.connection_status.connect(self.connection_status)
        self.worker.moveToThread(self)
    
    def run(self):
        """Запуск потока"""
        self.worker.start()
        self.exec_()
    
    def stop(self):
        """Остановка потока"""
        self.worker.stop()
        self.quit()
        self.wait()
    
    def set_demo_mode(self, enabled: bool):
        """Переключение демо-режима"""
        self.worker.set_demo_mode(enabled)
    
    def set_recording(self, enabled: bool):
        """Включение записи"""
        self.worker.set_recording(enabled)
    
    def reset_peak(self):
        """Сброс пиков"""
        self.worker.reset_peak()
    
    def get_last_data(self) -> Dict[str, Any]:
        """Получить последние данные"""
        return self.worker.get_last_data()

# ============================================
# ТЕСТОВЫЙ ЗАПУСК
# ============================================

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    print("🧪 Тест Hardware Worker")
    print("=" * 40)
    
    # Создаём поток
    thread = HardwareThread(demo_mode=True)
    thread.data_updated.connect(lambda data: print(f"📊 Данные: RPM={data.get('rpm', 0)}"))
    thread.start()
    
    # Ждём 3 секунды
    import time
    time.sleep(3)
    
    print("\n🔄 Переключение в реальный режим...")
    thread.set_demo_mode(False)
    time.sleep(1)
    
    print("\n🛑 Остановка...")
    thread.stop()
    print("✅ Тест завершён")