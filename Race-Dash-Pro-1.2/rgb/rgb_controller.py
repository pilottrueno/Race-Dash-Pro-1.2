#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading

class RGBController:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, led_count=29, gpio_pin=18, brightness=0.4):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self.led_count = led_count
        self.gpio_pin = gpio_pin
        self.pixels = None
        self.is_available = False
        self.brightness = brightness
        self.last_rpm = -1
        self.running = False
        self._thread = None
        self._demo_mode = False
        
        self._init_hardware()
    
    def _init_hardware(self):
        try:
            import board
            import neopixel
            pin = getattr(board, f'D{self.gpio_pin}')
            time.sleep(0.05)
            self.pixels = neopixel.NeoPixel(pin, self.led_count, brightness=self.brightness, auto_write=False)
            self.is_available = True
            print(f"✅ RGB-лента: {self.led_count} LED на GPIO {self.gpio_pin}")
        except ImportError:
            print("⚠️ neopixel не установлен")
            self.is_available = False
        except Exception as e:
            print(f"⚠️ Ошибка RGB: {e}")
            self.is_available = False
    
    def test_mode(self):
        if not self.is_available or self.pixels is None:
            print("⚠️ Лента недоступна для теста")
            return
        
        print("🔄 Тест ленты: бегущий огонёк")
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        
        for color in colors:
            for i in range(self.led_count):
                self.pixels[i] = (color[0] << 16) | (color[1] << 8) | color[2]
                self.pixels.show()
                time.sleep(0.02)
                if i > 0:
                    self.pixels[i-1] = 0
                    self.pixels.show()
        
        for color in reversed(colors):
            for i in range(self.led_count - 1, -1, -1):
                self.pixels[i] = (color[0] << 16) | (color[1] << 8) | color[2]
                self.pixels.show()
                time.sleep(0.02)
                if i < self.led_count - 1:
                    self.pixels[i+1] = 0
                    self.pixels.show()
        
        self.clear()
        time.sleep(0.3)
        print("✅ Тест ленты завершён")
    
    def set_shift_lights(self, rpm, max_rpm=8000):
        if not self.is_available or self.pixels is None:
            return
        if rpm == self.last_rpm:
            return
        self.last_rpm = rpm
        
        for i in range(self.led_count):
            self.pixels[i] = 0
        
        percent = min(1.0, rpm / max_rpm)
        count = int(percent * self.led_count)
        
        if rpm > 7500:
            color = (255, 0, 0)
        elif rpm > 6500:
            color = (255, 100, 0)
        elif rpm > 5000:
            color = (255, 200, 0)
        elif rpm > 3000:
            color = (0, 255, 0)
        else:
            color = (0, 100, 255)
        
        color_int = (color[0] << 16) | (color[1] << 8) | color[2]
        
        for i in range(count):
            self.pixels[i] = color_int
        
        self.pixels.show()
    
    def clear(self):
        if self.is_available and self.pixels is not None:
            for i in range(self.led_count):
                self.pixels[i] = 0
            self.pixels.show()
    
    def cleanup(self):
        """Максимально агрессивное выключение ленты"""
        if self.pixels is not None:
            try:
                for i in range(self.led_count):
                    self.pixels[i] = 0
                self.pixels.show()
                self.pixels.deinit()
                print("🛑 RGB-лента выключена (cleanup)")
            except Exception as e:
                print(f"⚠️ Ошибка при выключении ленты: {e}")
            finally:
                self.pixels = None
                self.is_available = False
        
        # Дополнительная очистка через прямой доступ
        try:
            import board
            import neopixel
            pin = getattr(board, f'D{self.gpio_pin}')
            pixels = neopixel.NeoPixel(pin, self.led_count, brightness=self.brightness)
            for i in range(self.led_count):
                pixels[i] = 0
            pixels.show()
            pixels.deinit()
        except:
            pass
    
    def __del__(self):
        self.cleanup()
