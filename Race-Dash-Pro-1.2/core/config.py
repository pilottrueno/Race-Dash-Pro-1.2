#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

class ConfigManager:
    """Менеджер настроек"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.themes = [
            {"name": "Dark Carbon", "bg": "#0a0f1a", "accent": "#00ffff"},
            {"name": "Racing Red", "bg": "#1a0a0a", "accent": "#ff3366"},
            {"name": "Cyber Blue", "bg": "#0a0a1a", "accent": "#4488ff"},
            {"name": "Racing Green", "bg": "#0a1a0a", "accent": "#44ff88"},
        ]
        self.current_theme_index = 0
        self._load()
    
    def _load(self):
        """Загрузка из файла"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.current_theme_index = data.get("theme", 0)
            except:
                pass
    
    def _save(self):
        """Сохранение в файл"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({"theme": self.current_theme_index}, f)
        except:
            pass
    
    def get_theme(self):
        """Получить текущую тему"""
        return self.themes[self.current_theme_index % len(self.themes)]
    
    def next_theme(self):
        """Следующая тема"""
        self.current_theme_index += 1
        self._save()
    
    def get(self, key, default=None):
        """Получить любой параметр"""
        return getattr(self, key, default)