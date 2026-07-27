from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty

class Gauge(QWidget):
    def __init__(self, title, unit, color, max_val=100, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.color = color
        self.max_val = max_val
        self._value = 0

        self.setMinimumSize(200, 140)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: #8a8f99; font-size: 15px; font-weight: 600;")
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        value_layout = QHBoxLayout()
        value_layout.setAlignment(Qt.AlignCenter)
        value_layout.setSpacing(4)
        
        self.value_label = QLabel("0.0")
        self.value_label.setStyleSheet(f"color: white; font-size: 46px; font-weight: 900; font-family: Monospace;")
        value_layout.addWidget(self.value_label)
        
        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet(f"color: #cccccc; font-size: 18px; font-weight: 600;")
        value_layout.addWidget(self.unit_label)
        
        layout.addLayout(value_layout)

        self.animation = QPropertyAnimation(self, b'value')
        self.animation.setDuration(300)

    @pyqtProperty(float)
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = max(0, min(self.max_val, v))
        self.value_label.setText(f"{self._value:.1f}")
        self.update()

    def set_value_animated(self, new_value):
        self.animation.stop()
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(new_value)
        self.animation.start()
