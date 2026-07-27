#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Стандартные OBD-II PID коды
"""

OBD_PIDS = {
    # Режим 01 - Текущие данные
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
}

# Режим 02 - Замороженные кадры
# Режим 03 - Диагностические коды
# Режим 04 - Очистка кодов

class OBDDecoder:
    """Декодирование OBD-II данных"""
    
    @staticmethod
    def decode_rpm(data):
        return (data[0] * 256 + data[1]) / 4
    
    @staticmethod
    def decode_speed(data):
        return data[0]
    
    @staticmethod
    def decode_coolant(data):
        return data[0] - 40
    
    @staticmethod
    def decode_tps(data):
        return (data[0] / 255) * 100
    
    @staticmethod
    def decode_lambda(data):
        return data[0] / 200.0
    
    @staticmethod
    def decode_voltage(data):
        return data[0] * 0.1
