#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject, pyqtSignal

class StateMachine(QObject):
    """Конечный автомат"""
    
    state_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._state = "BOOTING"
        self._states = {
            "BOOTING": ["HARDWARE_CHECK", "IDLE", "SHUTDOWN"],
            "HARDWARE_CHECK": ["IDLE", "SHUTDOWN"],
            "IDLE": ["DRIVING", "ALARM", "SHUTDOWN"],
            "DRIVING": ["IDLE", "ALARM", "SHUTDOWN"],
            "ALARM": ["IDLE", "SHUTDOWN"],
            "SHUTDOWN": []
        }
    
    @property
    def state(self):
        return self._state
    
    def transition(self, new_state):
        """Переход в новое состояние"""
        if new_state == self._state:
            return
        if new_state not in self._states.get(self._state, []):
            print(f"⚠️ Недопустимый переход: {self._state} -> {new_state}")
            return
        old_state = self._state
        self._state = new_state
        self.state_changed.emit(new_state)
        print(f"🔄 Состояние: {old_state} -> {new_state}")