#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RGB Controller — Управление светодиодной лентой WS2812/SK6812
Поддерживает: GPIO 18, 29 светодиодов (настраивается)
"""

import time
import threading
import atexit
from typing import Optional, Tuple, List

# ============================================================
# БАЗОВЫЙ КЛАСС (СИНГЛТОН)
# ============================================================

class RGBController:
    """
    Контроллер RGB-ленты (синглтон).
    Один экземпляр для всего приложения.
    """

    _instance: Optional['RGBController'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        led_count: int = 29,
        gpio_pin: int = 18,
        brightness: float = 0.5,
        auto_test: bool = True
    ):
        # Защита от повторной инициализации
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        self.led_count = led_count
        self.gpio_pin = gpio_pin
        self.brightness = max(0.0, min(1.0, brightness))

        self._pixels = None
        self._available = False
        self._last_rpm = -1
        self._running = False
        self._demo_thread = None
        self._demo_active = False

        self._init_hardware()

        # Тест при запуске
        if auto_test and self._available:
            self.test_mode()

        # Регистрируем очистку при завершении
        atexit.register(self.cleanup)

    # ============================================================
    # ИНИЦИАЛИЗАЦИЯ
    # ============================================================

    def _init_hardware(self) -> None:
        """Инициализация аппаратной части ленты."""
        try:
            import board
            import neopixel

            pin = getattr(board, f'D{self.gpio_pin}')
            self._pixels = neopixel.NeoPixel(
                pin,
                self.led_count,
                brightness=self.brightness,
                auto_write=False
            )
            self._available = True
            print(f"✅ RGB-лента: {self.led_count} LED на GPIO {self.gpio_pin}")

        except ImportError:
            print("⚠️ neopixel не установлен. Установка: pip install adafruit-circuitpython-neopixel")
            self._available = False

        except Exception as e:
            print(f"⚠️ Ошибка RGB: {e}")
            self._available = False

    # ============================================================
    # ОСНОВНЫЕ МЕТОДЫ
    # ============================================================

    def set_shift_lights(self, rpm: int, max_rpm: int = 8000) -> None:
        """
        Обновление цвета ленты по оборотам.
        """
        if not self._available or self._pixels is None:
            return

        if rpm == self._last_rpm:
            return
        self._last_rpm = rpm

        # Очистка
        for i in range(self.led_count):
            self._pixels[i] = 0

        percent = min(1.0, rpm / max_rpm)
        count = int(percent * self.led_count)

        # Выбор цвета
        if rpm > 7500:
            color = (255, 0, 0)       # Красный
        elif rpm > 6500:
            color = (255, 100, 0)     # Оранжевый
        elif rpm > 5000:
            color = (255, 200, 0)     # Жёлтый
        elif rpm > 3000:
            color = (0, 255, 0)       # Зелёный
        else:
            color = (0, 100, 255)     # Синий

        color_int = (color[0] << 16) | (color[1] << 8) | color[2]

        for i in range(count):
            self._pixels[i] = color_int

        self._pixels.show()

    def set_color(self, rgb: Tuple[int, int, int], index: Optional[int] = None) -> None:
        """
        Установить цвет на один или все светодиоды.
        """
        if not self._available or self._pixels is None:
            return

        r, g, b = rgb
        color_int = (r << 16) | (g << 8) | b

        if index is None:
            for i in range(self.led_count):
                self._pixels[i] = color_int
        elif 0 <= index < self.led_count:
            self._pixels[index] = color_int

        self._pixels.show()

    def clear(self) -> None:
        """Выключить все светодиоды."""
        if not self._available or self._pixels is None:
            return
        for i in range(self.led_count):
            self._pixels[i] = 0
        self._pixels.show()

    # ============================================================
    # ТЕСТ
    # ============================================================

    def test_mode(self, duration: float = 2.0) -> None:
        """
        Бегущий огонёк: проверка всех светодиодов.
        """
        if not self._available or self._pixels is None:
            print("⚠️ Лента недоступна для теста")
            return

        print("🔄 Тест ленты: бегущий огонёк")
        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
        ]

        steps = 4
        delay = duration / (self.led_count * steps)

        for color in colors:
            for i in range(self.led_count):
                self._pixels[i] = (color[0] << 16) | (color[1] << 8) | color[2]
                self._pixels.show()
                time.sleep(delay)
                if i > 0:
                    self._pixels[i - 1] = 0
                    self._pixels.show()

        for color in reversed(colors):
            for i in range(self.led_count - 1, -1, -1):
                self._pixels[i] = (color[0] << 16) | (color[1] << 8) | color[2]
                self._pixels.show()
                time.sleep(delay)
                if i < self.led_count - 1:
                    self._pixels[i + 1] = 0
                    self._pixels.show()

        self.clear()
        time.sleep(0.2)
        print("✅ Тест ленты завершён")

    # ============================================================
    # ДЕМО-РЕЖИМ (ФОНОВЫЙ)
    # ============================================================

    def start_demo(self, duration: float = 30.0) -> None:
        """
        Запустить демо-режим: бегущие огни в фоновом потоке.
        """
        if not self._available:
            print("⚠️ Лента недоступна")
            return

        if self._demo_active:
            self.stop_demo()

        self._demo_active = True
        self._demo_thread = threading.Thread(
            target=self._demo_loop,
            args=(duration,),
            daemon=True
        )
        self._demo_thread.start()
        print("🎬 Демо-режим запущен")

    def stop_demo(self) -> None:
        """Остановить демо-режим."""
        self._demo_active = False
        if self._demo_thread and self._demo_thread.is_alive():
            self._demo_thread.join(timeout=0.5)
        self.clear()
        print("⏹ Демо-режим остановлен")

    def _demo_loop(self, duration: float) -> None:
        """Цикл демо-режима (выполняется в потоке)."""
        colors = [
            (255, 0, 0),
            (255, 100, 0),
            (255, 200, 0),
            (0, 255, 0),
            (0, 100, 255),
            (255, 0, 255),
        ]

        start_time = time.time()
        while self._demo_active and (time.time() - start_time < duration):
            for color in colors:
                if not self._demo_active:
                    break
                self.set_color(color)
                time.sleep(0.3)

        if self._demo_active:
            self.clear()
            self._demo_active = False
            print("🎬 Демо-режим завершён")

    # ============================================================
    # ОЧИСТКА
    # ============================================================

    def cleanup(self) -> None:
        """Полное отключение ленты и освобождение ресурсов."""
        if self._pixels is not None:
            try:
                self.clear()
                self._pixels.deinit()
                print("🛑 RGB-лента выключена")
            except Exception as e:
                print(f"⚠️ Ошибка при выключении ленты: {e}")
            finally:
                self._pixels = None
                self._available = False
                self._demo_active = False

# ============================================================
# ТЕСТОВЫЙ ЗАПУСК
# ============================================================

if __name__ == '__main__':
    print("🧪 Тест RGB Controller")
    print("=" * 40)

    # Создаём контроллер
    rgb = RGBController(led_count=29, gpio_pin=18)

    if not rgb._available:
        print("❌ Лента недоступна")
        exit(1)

    # Тест
    rgb.test_mode(duration=1.5)

    # Демо
    rgb.start_demo(duration=5.0)
    time.sleep(5.0)
    rgb.stop_demo()

    # Очистка
    rgb.cleanup()
    print("✅ Тест завершён")