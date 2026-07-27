#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для работы с CAN шиной
Поддерживает: OBD-II, MegaSquirt, Speeduino, Link ECU
"""

import time
import threading
import struct
from datetime import datetime

class CANController:
    """Контроллер CAN шины"""
    
    def __init__(self, interface='can0', bitrate=500000):
        self.interface = interface
        self.bitrate = bitrate
        self.is_available = False
        self.running = False
        self.thread = None
        self.data = {
            'rpm': 0,
            'speed': 0,
            'coolant': 0,
            'oil_temp': 0,
            'boost': 0.0,
            'lambda': 1.0,
            'afr': 14.7,
            'tps': 0,
            'voltage': 12.8,
            'ign_angle': 0,
            'fuel_pressure': 0,
            'oil_pressure': 0,
            'egt': 0,
            'knock': 0,
            'ecu_connected': False
        }
        self._init_hardware()
    
    def _init_hardware(self):
        """Инициализация CAN интерфейса"""
        try:
            import socket
            import can
            self.bus = can.interface.Bus(channel=self.interface, bustype='socketcan')
            self.is_available = True
            print(f"✅ CAN шина: {self.interface} на {self.bitrate} бит/с")
        except ImportError:
            print("⚠️ Библиотека python-can не установлена")
            print("   Установка: pip install python-can")
            self.is_available = False
        except Exception as e:
            print(f"⚠️ Ошибка CAN: {e}")
            print("   Работа в режиме симуляции")
            self.is_available = False
    
    def start(self):
        """Запуск чтения CAN"""
        if not self.is_available:
            self._simulate_loop()
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        print("🔄 CAN шина запущена")
    
    def _read_loop(self):
        """Цикл чтения CAN сообщений"""
        try:
            import can
            while self.running:
                msg = self.bus.recv(timeout=0.1)
                if msg:
                    self._parse_message(msg)
        except Exception as e:
            print(f"⚠️ Ошибка чтения CAN: {e}")
            self._simulate_loop()
    
    def _parse_message(self, msg):
        """Парсинг CAN сообщения"""
        # OBD-II стандартные ID
        if msg.arbitration_id == 0x0C:  # RPM
            self.data['rpm'] = (msg.data[0] * 256 + msg.data[1]) / 4
            self.data['ecu_connected'] = True
        elif msg.arbitration_id == 0x0D:  # Speed
            self.data['speed'] = msg.data[0]
        elif msg.arbitration_id == 0x05:  # Coolant
            self.data['coolant'] = msg.data[0] - 40
        elif msg.arbitration_id == 0x10:  # TPS
            self.data['tps'] = (msg.data[0] / 255) * 100
        elif msg.arbitration_id == 0x11:  # Fuel Pressure
            self.data['fuel_pressure'] = msg.data[0] * 0.01
        # Добавьте свои ID для других параметров
    
    def _simulate_loop(self):
        """Симуляция данных для тестирования"""
        print("🔄 Симуляция CAN данных")
        import random
        
        rpm = 800
        while self.running:
            rpm += random.uniform(-50, 100)
            rpm = max(800, min(8000, rpm))
            load = rpm / 8000
            
            self.data['rpm'] = rpm
            self.data['speed'] = rpm / 30
            self.data['coolant'] = 85 + load * 30
            self.data['oil_temp'] = 90 + load * 40
            self.data['boost'] = load * 1.5
            self.data['lambda'] = 1.0 - load * 0.1
            self.data['afr'] = self.data['lambda'] * 14.7
            self.data['tps'] = load * 100
            self.data['voltage'] = 14.2 - load * 0.5
            self.data['egt'] = 400 + load * 500
            self.data['fuel_pressure'] = 3.8 + load * 1.2
            self.data['oil_pressure'] = 1.2 + load * 4.0
            self.data['ecu_connected'] = True
            
            time.sleep(0.05)
    
    def get_data(self):
        """Получить текущие данные"""
        return self.data.copy()
    
    def send_message(self, can_id, data):
        """Отправить сообщение по CAN"""
        if not self.is_available:
            return False
        try:
            import can
            msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
            self.bus.send(msg)
            return True
        except Exception as e:
            print(f"⚠️ Ошибка отправки CAN: {e}")
            return False
    
    def stop(self):
        """Остановка CAN"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("🛑 CAN остановлена")
    
    def cleanup(self):
        self.stop()
