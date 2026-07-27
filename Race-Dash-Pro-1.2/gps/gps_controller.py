#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль управления GPS-модулем для Race Dash Pro
Поддерживает NMEA-совместимые GPS-модули (UART)
"""

import time
import threading
import serial
from datetime import datetime

class GPSController:
    """Контроллер GPS-модуля"""
    
    def __init__(self, port='/dev/ttyAMA0', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.is_available = False
        self.running = False
        self.thread = None
        
        # Данные GPS
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.speed = 0.0  # км/ч
        self.satellites = 0
        self.fix = False
        self.time_str = ""
        self.date_str = ""
        
        self._init_hardware()
    
    def _init_hardware(self):
        """Инициализация GPS-модуля"""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_available = True
            print(f"✅ GPS-модуль: {self.port} на {self.baudrate} бод")
        except Exception as e:
            print(f"⚠️ Ошибка GPS: {e}")
            print("   GPS будет работать в симуляционном режиме")
            self.is_available = False
    
    def start(self):
        """Запуск чтения GPS"""
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        print("🛰️ GPS запущен")
    
    def _read_loop(self):
        """Цикл чтения GPS-данных"""
        if not self.is_available:
            self._simulate_loop()
            return
        
        try:
            import pynmea2
            while self.running:
                line = self.serial.readline().decode('ascii', errors='ignore')
                if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                    try:
                        msg = pynmea2.parse(line)
                        if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                            self.latitude = msg.latitude
                            self.longitude = msg.longitude
                            self.fix = True
                        if hasattr(msg, 'num_sats'):
                            self.satellites = msg.num_sats
                        if hasattr(msg, 'spd_over_grnd'):
                            self.speed = msg.spd_over_grnd * 1.852
                        if hasattr(msg, 'altitude'):
                            self.altitude = msg.altitude
                        if hasattr(msg, 'timestamp'):
                            self.time_str = str(msg.timestamp)
                    except:
                        pass
                time.sleep(0.1)
        except Exception as e:
            print(f"⚠️ Ошибка чтения GPS: {e}")
            self._simulate_loop()
    
    def _simulate_loop(self):
        """Симуляция GPS-данных для тестирования"""
        print("🔄 Симуляция GPS")
        lat = 55.7558
        lon = 37.6173
        speed = 0
        satellites = 0
        
        while self.running:
            # Простая симуляция движения
            speed = (speed + 0.5) % 80
            if speed > 5:
                lat += 0.0001 * (speed / 60)
                lon += 0.0001 * (speed / 60)
                satellites = 8
                self.fix = True
            else:
                satellites = 0
                self.fix = False
            
            self.latitude = lat
            self.longitude = lon
            self.speed = speed
            self.satellites = satellites
            self.altitude = 100.0
            
            time.sleep(0.5)
    
    def get_data(self):
        """Получить текущие GPS-данные"""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'speed': self.speed,
            'satellites': self.satellites,
            'fix': self.fix,
            'time': self.time_str,
            'date': self.date_str
        }
    
    def stop(self):
        """Остановка GPS"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.serial:
            self.serial.close()
        print("🛑 GPS остановлен")
    
    def cleanup(self):
        self.stop()
