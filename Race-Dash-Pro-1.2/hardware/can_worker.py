#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CAN Worker — Работа с CAN шиной автомобиля
Поддерживает: OBD-II, MegaSquirt, Speeduino, Link ECU, Haltech
"""

import time
import threading
import struct
from typing import Dict, Any, Optional, Callable
from enum import Enum

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ============================================

class CANProtocol(Enum):
    """Типы протоколов CAN"""
    OBD2 = 0
    MEGASQUIRT = 1
    SPEEDUINO = 2
    LINK_ECU = 3
    HALTECH = 4
    CUSTOM = 5

class CANStatus(Enum):
    """Статус подключения к CAN"""
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    ERROR = 3

class CANData:
    """Данные с CAN шины"""
    def __init__(self):
        self.rpm = 0
        self.speed = 0
        self.coolant = 0
        self.oil_temp = 0
        self.boost = 0.0
        self.tps = 0.0
        self.voltage = 0.0
        self.ign_angle = 0.0
        self.fuel_pressure = 0.0
        self.oil_pressure = 0.0
        self.egt = 0.0
        self.lambda_val = 1.0
        self.afr = 14.7
        self.knock = 0.0
        self.fuel_trim = 0.0
        self.maf = 0.0
        self.load = 0.0
        self.ecu_connected = False
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'rpm': self.rpm,
            'speed': self.speed,
            'coolant': self.coolant,
            'oil_temp': self.oil_temp,
            'boost': self.boost,
            'tps': self.tps,
            'voltage': self.voltage,
            'ign_angle': self.ign_angle,
            'fuel_pressure': self.fuel_pressure,
            'oil_pressure': self.oil_pressure,
            'egt': self.egt,
            'lambda': self.lambda_val,
            'afr': self.afr,
            'knock': self.knock,
            'fuel_trim': self.fuel_trim,
            'maf': self.maf,
            'load': self.load,
            'ecu_connected': self.ecu_connected,
        }

# ============================================
# OBD-II ПРОТОКОЛ
# ============================================

class OBD2Protocol:
    """OBD-II протокол"""
    
    # OBD-II PID коды
    PIDS = {
        'rpm': 0x0C,
        'speed': 0x0D,
        'coolant': 0x05,
        'fuel_pressure': 0x0A,
        'intake_temp': 0x0F,
        'maf': 0x10,
        'tps': 0x11,
        'timing_advance': 0x0E,
        'lambda': 0x34,
        'fuel_trim': 0x06,
        'voltage': 0x42,
        'load': 0x04,
        'fuel_level': 0x2F,
        'engine_run_time': 0x1F,
        'distance_since_dtc': 0x21,
    }
    
    @staticmethod
    def decode_rpm(data: bytes) -> int:
        """Расшифровка RPM из OBD-II ответа"""
        if len(data) >= 2:
            return (data[0] * 256 + data[1]) // 4
        return 0
    
    @staticmethod
    def decode_speed(data: bytes) -> int:
        """Расшифровка скорости"""
        return data[0] if len(data) >= 1 else 0
    
    @staticmethod
    def decode_coolant(data: bytes) -> int:
        """Расшифровка температуры ОЖ"""
        return data[0] - 40 if len(data) >= 1 else 0
    
    @staticmethod
    def decode_tps(data: bytes) -> float:
        """Расшифровка положения дросселя"""
        return (data[0] / 255) * 100 if len(data) >= 1 else 0
    
    @staticmethod
    def decode_lambda(data: bytes) -> float:
        """Расшифровка Lambda"""
        return data[0] / 200.0 if len(data) >= 1 else 0
    
    @staticmethod
    def decode_voltage(data: bytes) -> float:
        """Расшифровка напряжения"""
        return data[0] * 0.1 if len(data) >= 1 else 0
    
    @staticmethod
    def decode_load(data: bytes) -> float:
        """Расшифровка нагрузки"""
        return (data[0] / 255) * 100 if len(data) >= 1 else 0

# ============================================
# MEGASQUIRT ПРОТОКОЛ
# ============================================

class MegaSquirtProtocol:
    """MegaSquirt протокол"""
    
    # Команды для MegaSquirt
    COMMANDS = {
        'rpm': b'\x81\x29\xC1\x00\x00\x00\x00\x00',
        'coolant': b'\x81\x29\xC2\x00\x00\x00\x00\x00',
        'tps': b'\x81\x29\xC3\x00\x00\x00\x00\x00',
        'map': b'\x81\x29\xC4\x00\x00\x00\x00\x00',
        'lambda': b'\x81\x29\xC5\x00\x00\x00\x00\x00',
        'battery': b'\x81\x29\xC6\x00\x00\x00\x00\x00',
        'egt': b'\x81\x29\xC7\x00\x00\x00\x00\x00',
    }
    
    @staticmethod
    def decode_rpm(data: bytes) -> int:
        """Расшифровка RPM из MegaSquirt"""
        if len(data) >= 2:
            return data[0] * 256 + data[1]
        return 0
    
    @staticmethod
    def decode_coolant(data: bytes) -> int:
        """Расшифровка температуры ОЖ"""
        return data[0] if len(data) >= 1 else 0
    
    @staticmethod
    def decode_tps(data: bytes) -> float:
        """Расшифровка TPS"""
        return (data[0] / 255) * 100 if len(data) >= 1 else 0
    
    @staticmethod
    def decode_map(data: bytes) -> float:
        """Расшифровка MAP (давление)"""
        return data[0] * 0.1 if len(data) >= 1 else 0

# ============================================
# ОСНОВНОЙ КЛАСС CAN WORKER
# ============================================

class CANWorker:
    """
    Асинхронная работа с CAN шиной
    Поддерживает различные протоколы
    """
    
    def __init__(self, interface: str = 'can0', protocol: CANProtocol = CANProtocol.OBD2):
        """
        Инициализация CAN Worker
        
        Args:
            interface: имя интерфейса (can0, vcan0, etc.)
            protocol: тип протокола (OBD2, MegaSquirt, etc.)
        """
        self.interface = interface
        self.protocol = protocol
        self.bus = None
        self.status = CANStatus.DISCONNECTED
        self.running = False
        self.thread = None
        
        # Данные
        self.data = CANData()
        
        # Callback для обновления данных
        self.on_data_updated: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Инициализация
        self._init_bus()
    
    # ============================================
    # ИНИЦИАЛИЗАЦИЯ
    # ============================================
    
    def _init_bus(self):
        """Инициализация CAN интерфейса"""
        try:
            import can
            self.bus = can.interface.Bus(channel=self.interface, bustype='socketcan')
            self.status = CANStatus.CONNECTED
            print(f"✅ CAN шина: {self.interface}, протокол: {self.protocol.name}")
        except ImportError:
            print("⚠️ Библиотека python-can не установлена")
            print("   Установка: pip install python-can")
            self.status = CANStatus.ERROR
        except Exception as e:
            print(f"⚠️ Ошибка CAN: {e}")
            self.status = CANStatus.ERROR
    
    # ============================================
    # ЗАПУСК И ОСТАНОВКА
    # ============================================
    
    def start(self):
        """Запуск чтения CAN"""
        if self.status == CANStatus.ERROR:
            print("❌ CAN не инициализирован")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        print("🔄 CAN чтение запущено")
    
    def stop(self):
        """Остановка чтения CAN"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("🛑 CAN чтение остановлено")
    
    # ============================================
    # ЦИКЛ ЧТЕНИЯ
    # ============================================
    
    def _read_loop(self):
        """Основной цикл чтения CAN сообщений"""
        if self.bus is None:
            self._simulate_data()
            return
        
        try:
            import can
            while self.running:
                # Чтение сообщения с таймаутом
                msg = self.bus.recv(timeout=0.1)
                if msg:
                    self._process_message(msg)
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            self._simulate_data()
    
    def _process_message(self, msg):
        """Обработка CAN сообщения"""
        # OBD-II
        if self.protocol == CANProtocol.OBD2:
            self._process_obd2(msg)
        # MegaSquirt
        elif self.protocol == CANProtocol.MEGASQUIRT:
            self._process_megasquirt(msg)
        # Speeduino
        elif self.protocol == CANProtocol.SPEEDUINO:
            self._process_speeduino(msg)
        # Другие протоколы
        else:
            self._process_custom(msg)
        
        # Обновление времени
        self.data.timestamp = time.time()
        self.data.ecu_connected = True
        
        # Вызов колбэка
        if self.on_data_updated:
            self.on_data_updated(self.data.to_dict())
    
    # ============================================
    # ОБРАБОТКА ПРОТОКОЛОВ
    # ============================================
    
    def _process_obd2(self, msg):
        """Обработка OBD-II сообщения"""
        # OBD-II ответы приходят на ID 0x7E8-0x7EF
        if 0x7E8 <= msg.arbitration_id <= 0x7EF:
            pid = msg.data[1]
            
            if pid == OBD2Protocol.PIDS['rpm']:
                self.data.rpm = OBD2Protocol.decode_rpm(msg.data[2:4])
            elif pid == OBD2Protocol.PIDS['speed']:
                self.data.speed = OBD2Protocol.decode_speed(msg.data[2:3])
            elif pid == OBD2Protocol.PIDS['coolant']:
                self.data.coolant = OBD2Protocol.decode_coolant(msg.data[2:3])
            elif pid == OBD2Protocol.PIDS['tps']:
                self.data.tps = OBD2Protocol.decode_tps(msg.data[2:3])
            elif pid == OBD2Protocol.PIDS['lambda']:
                self.data.lambda_val = OBD2Protocol.decode_lambda(msg.data[2:3])
                self.data.afr = self.data.lambda_val * 14.7
            elif pid == OBD2Protocol.PIDS['voltage']:
                self.data.voltage = OBD2Protocol.decode_voltage(msg.data[2:3])
            elif pid == OBD2Protocol.PIDS['load']:
                self.data.load = OBD2Protocol.decode_load(msg.data[2:3])
    
    def _process_megasquirt(self, msg):
        """Обработка MegaSquirt сообщения"""
        # MegaSquirt ответы на ID 0x6B1
        if msg.arbitration_id == 0x6B1:
            cmd = msg.data[1]
            
            if cmd == 0xC1:  # RPM
                self.data.rpm = MegaSquirtProtocol.decode_rpm(msg.data[2:4])
            elif cmd == 0xC2:  # Coolant
                self.data.coolant = MegaSquirtProtocol.decode_coolant(msg.data[2:3])
            elif cmd == 0xC3:  # TPS
                self.data.tps = MegaSquirtProtocol.decode_tps(msg.data[2:3])
            elif cmd == 0xC4:  # MAP
                self.data.boost = MegaSquirtProtocol.decode_map(msg.data[2:3])
    
    def _process_speeduino(self, msg):
        """Обработка Speeduino сообщения"""
        # Speeduino использует похожий на MegaSquirt протокол
        self._process_megasquirt(msg)
    
    def _process_custom(self, msg):
        """Обработка пользовательского протокола"""
        # Здесь можно добавить свою логику
        pass
    
    # ============================================
    # СИМУЛЯЦИЯ
    # ============================================
    
    def _simulate_data(self):
        """Симуляция данных для тестирования"""
        import random
        
        while self.running:
            # Симуляция работы двигателя
            rpm = 800 + random.randint(-50, 100)
            rpm = max(800, min(8000, rpm))
            
            load = rpm / 8000
            
            self.data.rpm = rpm
            self.data.speed = int(rpm / 30)
            self.data.coolant = int(85 + load * 40)
            self.data.oil_temp = int(90 + load * 50)
            self.data.boost = round(load * 1.5, 2)
            self.data.tps = round(load * 100, 1)
            self.data.voltage = round(14.2 - load * 0.8, 1)
            self.data.lambda_val = round(1.0 - load * 0.1, 3)
            self.data.afr = round(self.data.lambda_val * 14.7, 1)
            self.data.egt = int(400 + load * 600)
            self.data.load = round(load * 100, 1)
            self.data.ecu_connected = True
            self.data.timestamp = time.time()
            
            if self.on_data_updated:
                self.on_data_updated(self.data.to_dict())
            
            time.sleep(0.05)
    
    # ============================================
    # ОТПРАВКА СООБЩЕНИЙ
    # ============================================
    
    def send_message(self, can_id: int, data: bytes) -> bool:
        """Отправка сообщения по CAN"""
        if self.bus is None:
            return False
        
        try:
            import can
            msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
            self.bus.send(msg)
            return True
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            return False
    
    def send_obd2_request(self, pid: int) -> bool:
        """Отправка OBD-II запроса"""
        # OBD-II запрос: 0x7DF
        data = bytes([0x02, 0x01, pid, 0x00, 0x00, 0x00, 0x00, 0x00])
        return self.send_message(0x7DF, data)
    
    def send_megasquirt_command(self, cmd: str) -> bool:
        """Отправка команды MegaSquirt"""
        if cmd in MegaSquirtProtocol.COMMANDS:
            return self.send_message(0x6B0, MegaSquirtProtocol.COMMANDS[cmd])
        return False

# ============================================
# ТЕСТОВЫЙ ЗАПУСК
# ============================================

if __name__ == '__main__':
    print("🧪 Тест CAN Worker")
    print("=" * 40)
    
    # Создаём CAN Worker в режиме симуляции
    worker = CANWorker(interface='vcan0', protocol=CANProtocol.OBD2)
    
    # Определяем callback
    def on_data(data):
        print(f"📊 RPM: {data['rpm']}, Speed: {data['speed']}, Coolant: {data['coolant']}°C")
    
    worker.on_data_updated = on_data
    
    # Запускаем
    worker.start()
    
    # Ждём 5 секунд
    time.sleep(5)
    
    # Останавливаем
    worker.stop()
    print("✅ Тест завершён")