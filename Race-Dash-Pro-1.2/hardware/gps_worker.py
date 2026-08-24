#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPS Worker — Работа с GPS модулем
Поддерживает: NMEA-совместимые GPS (UART)
"""

import time
import threading
import math
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ============================================

class GPSStatus(Enum):
    """Статус GPS модуля"""
    DISCONNECTED = 0
    SEARCHING = 1
    FIX_2D = 2
    FIX_3D = 3
    ERROR = 4

class GPSData:
    """Данные с GPS модуля"""
    def __init__(self):
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.speed = 0.0          # км/ч
        self.course = 0.0         # градусы
        self.satellites = 0
        self.fix = False
        self.fix_type = 0         # 0 = нет, 1 = 2D, 2 = 3D
        self.hdop = 99.9         # точность
        self.time = ""
        self.date = ""
        self.timestamp = time.time()
        self.status = GPSStatus.DISCONNECTED
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'speed': self.speed,
            'course': self.course,
            'satellites': self.satellites,
            'fix': self.fix,
            'fix_type': self.fix_type,
            'hdop': self.hdop,
            'time': self.time,
            'date': self.date,
        }
    
    def is_valid(self) -> bool:
        """Проверка валидности данных"""
        return self.fix and self.satellites >= 4

# ============================================
# NMEA ПАРСЕР
# ============================================

class NMEAParser:
    """Парсер NMEA сообщений"""
    
    @staticmethod
    def parse_gga(sentence: str) -> Optional[Dict]:
        """Парсинг $GPGGA (Global Positioning System Fix Data)"""
        parts = sentence.split(',')
        if len(parts) < 15:
            return None
        
        try:
            data = {}
            
            # Время UTC
            if parts[1]:
                t = parts[1]
                data['time'] = f"{t[:2]}:{t[2:4]}:{t[4:6]}"
            
            # Широта
            if parts[2] and parts[3]:
                lat = float(parts[2])
                lat_deg = int(lat / 100)
                lat_min = lat - lat_deg * 100
                data['latitude'] = lat_deg + lat_min / 60
                if parts[3] == 'S':
                    data['latitude'] = -data['latitude']
            
            # Долгота
            if parts[4] and parts[5]:
                lon = float(parts[4])
                lon_deg = int(lon / 100)
                lon_min = lon - lon_deg * 100
                data['longitude'] = lon_deg + lon_min / 60
                if parts[5] == 'W':
                    data['longitude'] = -data['longitude']
            
            # Качество фикса
            if parts[6]:
                data['fix_type'] = int(parts[6])
                data['fix'] = data['fix_type'] > 0
            
            # Количество спутников
            if parts[7]:
                data['satellites'] = int(parts[7])
            
            # HDOP (точность)
            if parts[8]:
                data['hdop'] = float(parts[8])
            
            # Высота
            if parts[9]:
                data['altitude'] = float(parts[9])
            
            return data
            
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def parse_rmc(sentence: str) -> Optional[Dict]:
        """Парсинг $GPRMC (Recommended Minimum Specific GNSS Data)"""
        parts = sentence.split(',')
        if len(parts) < 12:
            return None
        
        try:
            data = {}
            
            # Время
            if parts[1]:
                t = parts[1]
                data['time'] = f"{t[:2]}:{t[2:4]}:{t[4:6]}"
            
            # Статус (A = валидный)
            if parts[2]:
                data['fix'] = parts[2] == 'A'
            
            # Широта
            if parts[3] and parts[4]:
                lat = float(parts[3])
                lat_deg = int(lat / 100)
                lat_min = lat - lat_deg * 100
                data['latitude'] = lat_deg + lat_min / 60
                if parts[4] == 'S':
                    data['latitude'] = -data['latitude']
            
            # Долгота
            if parts[5] and parts[6]:
                lon = float(parts[5])
                lon_deg = int(lon / 100)
                lon_min = lon - lon_deg * 100
                data['longitude'] = lon_deg + lon_min / 60
                if parts[6] == 'W':
                    data['longitude'] = -data['longitude']
            
            # Скорость (узлы → км/ч)
            if parts[7]:
                data['speed'] = float(parts[7]) * 1.852
            
            # Курс
            if parts[8]:
                data['course'] = float(parts[8])
            
            # Дата
            if parts[9]:
                d = parts[9]
                data['date'] = f"{d[:2]}.{d[2:4]}.{d[4:6]}"
            
            return data
            
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def parse_gsa(sentence: str) -> Optional[Dict]:
        """Парсинг $GPGSA (GNSS DOP and Active Satellites)"""
        parts = sentence.split(',')
        if len(parts) < 18:
            return None
        
        try:
            data = {}
            
            # Режим (1 = нет, 2 = 2D, 3 = 3D)
            if parts[2]:
                data['fix_type'] = int(parts[2])
                data['fix'] = data['fix_type'] > 0
            
            # PDOP
            if parts[15]:
                data['pdop'] = float(parts[15])
            
            # HDOP
            if parts[16]:
                data['hdop'] = float(parts[16])
            
            # VDOP
            if parts[17]:
                data['vdop'] = float(parts[17])
            
            return data
            
        except (ValueError, IndexError):
            return None

# ============================================
# ОСНОВНОЙ КЛАСС GPS WORKER
# ============================================

class GPSWorker:
    """
    Асинхронная работа с GPS модулем
    Чтение данных через UART, парсинг NMEA
    """
    
    def __init__(self, port: str = '/dev/ttyAMA0', baudrate: int = 9600):
        """
        Инициализация GPS Worker
        
        Args:
            port: UART порт (ttyAMA0, ttyUSB0, etc.)
            baudrate: скорость (9600, 38400, 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.thread = None
        
        # Данные
        self.data = GPSData()
        
        # Callback для обновления данных
        self.on_data_updated: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Инициализация
        self._init_serial()
    
    # ============================================
    # ИНИЦИАЛИЗАЦИЯ
    # ============================================
    
    def _init_serial(self):
        """Инициализация UART"""
        try:
            import serial
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.data.status = GPSStatus.SEARCHING
            print(f"✅ GPS: {self.port} на {self.baudrate} бод")
        except ImportError:
            print("⚠️ Библиотека pyserial не установлена")
            print("   Установка: pip install pyserial")
            self.data.status = GPSStatus.ERROR
        except Exception as e:
            print(f"⚠️ Ошибка GPS: {e}")
            self.data.status = GPSStatus.ERROR
    
    # ============================================
    # ЗАПУСК И ОСТАНОВКА
    # ============================================
    
    def start(self):
        """Запуск чтения GPS"""
        if self.serial is None:
            print("❌ GPS не инициализирован")
            self._simulate()
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        print("🛰️ GPS чтение запущено")
    
    def stop(self):
        """Остановка чтения GPS"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.serial:
            self.serial.close()
        print("🛑 GPS чтение остановлено")
    
    # ============================================
    # ЦИКЛ ЧТЕНИЯ
    # ============================================
    
    def _read_loop(self):
        """Основной цикл чтения GPS данных"""
        try:
            import serial
            while self.running:
                line = self.serial.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$'):
                    self._process_sentence(line)
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            self._simulate()
    
    def _process_sentence(self, sentence: str):
        """Обработка NMEA предложения"""
        if sentence.startswith('$GPGGA'):
            parsed = NMEAParser.parse_gga(sentence)
            if parsed:
                self._update_data(parsed)
        
        elif sentence.startswith('$GPRMC'):
            parsed = NMEAParser.parse_rmc(sentence)
            if parsed:
                self._update_data(parsed)
        
        elif sentence.startswith('$GPGSA'):
            parsed = NMEAParser.parse_gsa(sentence)
            if parsed:
                self._update_data(parsed)
        
        # Вызов колбэка
        if self.on_data_updated:
            self.on_data_updated(self.data.to_dict())
    
    def _update_data(self, parsed: Dict):
        """Обновление данных GPS"""
        # Широта
        if 'latitude' in parsed:
            self.data.latitude = parsed['latitude']
        
        # Долгота
        if 'longitude' in parsed:
            self.data.longitude = parsed['longitude']
        
        # Высота
        if 'altitude' in parsed:
            self.data.altitude = parsed['altitude']
        
        # Скорость
        if 'speed' in parsed:
            self.data.speed = parsed['speed']
        
        # Курс
        if 'course' in parsed:
            self.data.course = parsed['course']
        
        # Количество спутников
        if 'satellites' in parsed:
            self.data.satellites = parsed['satellites']
        
        # Фиксация
        if 'fix' in parsed:
            self.data.fix = parsed['fix']
        
        if 'fix_type' in parsed:
            self.data.fix_type = parsed['fix_type']
            if self.data.fix_type == 0:
                self.data.status = GPSStatus.SEARCHING
            elif self.data.fix_type == 1:
                self.data.status = GPSStatus.FIX_2D
            elif self.data.fix_type >= 2:
                self.data.status = GPSStatus.FIX_3D
        
        # Точность
        if 'hdop' in parsed:
            self.data.hdop = parsed['hdop']
        
        # Время и дата
        if 'time' in parsed:
            self.data.time = parsed['time']
        if 'date' in parsed:
            self.data.date = parsed['date']
        
        self.data.timestamp = time.time()
    
    # ============================================
    # СИМУЛЯЦИЯ
    # ============================================
    
    def _simulate(self):
        """Симуляция GPS данных для тестирования"""
        import random
        
        # Начальные координаты (Москва)
        lat = 55.7558
        lon = 37.6173
        speed = 0
        satellites = 0
        
        while self.running:
            # Симуляция движения
            speed = (speed + 0.3) % 80
            
            if speed > 5:
                lat += 0.0001 * (speed / 60) * random.uniform(-0.5, 0.5)
                lon += 0.0001 * (speed / 60) * random.uniform(-0.5, 0.5)
                satellites = random.randint(6, 12)
                self.data.fix = True
                self.data.fix_type = 3
                self.data.status = GPSStatus.FIX_3D
            else:
                satellites = random.randint(0, 4)
                self.data.fix = satellites >= 4
                self.data.fix_type = 2 if self.data.fix else 0
                self.data.status = GPSStatus.FIX_2D if self.data.fix else GPSStatus.SEARCHING
            
            self.data.latitude = lat
            self.data.longitude = lon
            self.data.speed = speed
            self.data.satellites = satellites
            self.data.altitude = 100.0 + random.uniform(-10, 10)
            self.data.hdop = random.uniform(0.5, 2.0)
            self.data.timestamp = time.time()
            
            if self.on_data_updated:
                self.on_data_updated(self.data.to_dict())
            
            time.sleep(0.5)
    
    # ============================================
    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ
    # ============================================
    
    def get_distance_to(self, lat: float, lon: float) -> float:
        """
        Расчёт расстояния до точки (в километрах)
        
        Args:
            lat: широта точки
            lon: долгота точки
        
        Returns:
            Расстояние в километрах
        """
        if not self.data.fix:
            return 0.0
        
        R = 6371  # радиус Земли в км
        
        lat1 = math.radians(self.data.latitude)
        lon1 = math.radians(self.data.longitude)
        lat2 = math.radians(lat)
        lon2 = math.radians(lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def get_formatted_position(self) -> str:
        """Форматированная строка с координатами"""
        if not self.data.fix:
            return "Нет сигнала"
        
        lat_dir = 'N' if self.data.latitude >= 0 else 'S'
        lon_dir = 'E' if self.data.longitude >= 0 else 'W'
        
        return f"{abs(self.data.latitude):.6f}{lat_dir} {abs(self.data.longitude):.6f}{lon_dir}"
    
    def get_formatted_speed(self) -> str:
        """Форматированная строка со скоростью"""
        if not self.data.fix:
            return "---"
        return f"{self.data.speed:.1f} км/ч"

# ============================================
# ТЕСТОВЫЙ ЗАПУСК
# ============================================

if __name__ == '__main__':
    import sys
    
    print("🧪 Тест GPS Worker")
    print("=" * 40)
    
    # Создаём GPS Worker (в симуляционном режиме)
    gps = GPSWorker(port='/dev/ttyAMA0', baudrate=9600)
    
    # Определяем callback
    def on_data(data):
        status = "✅" if data['fix'] else "❌"
        print(f"{status} Sat: {data['satellites']}, Lat: {data['latitude']:.5f}, Lon: {data['longitude']:.5f}, Speed: {data['speed']:.1f} км/ч")
    
    gps.on_data_updated = on_data
    
    # Запускаем
    gps.start()
    
    # Ждём 10 секунд
    time.sleep(10)
    
    # Останавливаем
    gps.stop()
    print("✅ Тест завершён")