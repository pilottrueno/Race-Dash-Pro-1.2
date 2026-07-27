#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.current_log = []
        self.last_save_time = time.time()
        self.log_interval = 60
        self.is_running = True
        
        os.makedirs(log_dir, exist_ok=True)
        print(f"📁 Логи будут сохраняться в: {log_dir}")
    
    def log_data(self, data):
        if not self.is_running:
            return
        
        entry = {
            'timestamp': time.time(),
            'time_str': datetime.now().strftime("%H:%M:%S"),
            'data': data.copy()
        }
        self.current_log.append(entry)
        
        if time.time() - self.last_save_time >= self.log_interval:
            self.save_log()
    
    def save_log(self):
        if not self.current_log:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"log_{timestamp}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== RACE DASH PRO LOG ===\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 40 + "\n")
                
                if self.current_log:
                    first = self.current_log[0]
                    headers = ['Time'] + list(first['data'].keys())
                    f.write(" | ".join(headers) + "\n")
                    f.write("-" * 40 + "\n")
                    
                    for entry in self.current_log:
                        values = [entry['time_str']]
                        for key in list(first['data'].keys()):
                            val = entry['data'].get(key, 0)
                            if isinstance(val, float):
                                values.append(f"{val:.1f}")
                            else:
                                values.append(str(val))
                        f.write(" | ".join(values) + "\n")
                
                f.write("-" * 40 + "\n")
                f.write(f"Всего записей: {len(self.current_log)}\n")
            
            print(f"💾 Лог сохранён: {filename} ({len(self.current_log)} записей)")
            self.current_log = []
            self.last_save_time = time.time()
            
        except Exception as e:
            print(f"⚠️ Ошибка сохранения лога: {e}")
    
    def get_logs(self, count=10):
        logs = []
        try:
            files = sorted([f for f in os.listdir(self.log_dir) if f.endswith('.txt')], reverse=True)
            for f in files[:count]:
                filepath = os.path.join(self.log_dir, f)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                logs.append({
                    'name': f,
                    'size': size,
                    'time': mtime.strftime("%Y-%m-%d %H:%M:%S"),
                    'path': filepath
                })
        except Exception as e:
            print(f"⚠️ Ошибка чтения логов: {e}")
        return logs
    
    def clear(self):
        try:
            for f in os.listdir(self.log_dir):
                if f.endswith('.txt'):
                    os.remove(os.path.join(self.log_dir, f))
            self.current_log = []
            self.last_save_time = time.time()
            print("🗑️ Все логи удалены")
        except Exception as e:
            print(f"⚠️ Ошибка очистки логов: {e}")
    
    def stop(self):
        self.is_running = False
        if self.current_log:
            self.save_log()
        print("🛑 Логирование остановлено")
