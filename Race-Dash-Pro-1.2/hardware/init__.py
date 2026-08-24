#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hardware Package — Аппаратное обеспечение RACE DASH PRO
========================================================
Содержит модули для работы с оборудованием:
- worker.py      — асинхронный опрос датчиков
- can_worker.py  — CAN шина (опционально)
- gps_worker.py  — GPS модуль (опционально)
"""

from .worker import HardwareWorker, HardwareThread, SensorData, SensorStatus

__all__ = [
    'HardwareWorker',
    'HardwareThread',
    'SensorData',
    'SensorStatus',
]

__version__ = '1.2.0'
__author__ = 'Бухлаков Евгений'
__email__ = 'Bukhlakoff@yandex.ru'