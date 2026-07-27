from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty

class Sensor(QWidget):
    def __init__(self, label, unit, color, max_val=100, parent=None):
        super().__init__(parent)
        self.label = label
        self.unit = unit
        self.color = color
        self.max_val = max_val
        self._value = 0

        self.setFixedHeight(74)
        self.setMinimumWidth(200)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: #14171c;
                border-radius: 16px;
                border-left: 6px solid {color};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 10, 8)

        left = QVBoxLayout()
        self.label_label = QLabel(label)
        self.label_label.setStyleSheet("color: #8a8f99; font-size: 14px; font-weight: 600;")
        left.addWidget(self.label_label)

        value_layout = QHBoxLayout()
        value_layout.setSpacing(4)
        
        self.value_label = QLabel("0.0")
        self.value_label.setStyleSheet("color: white; font-size: 30px; font-weight: 800; font-family: Monospace;")
        value_layout.addWidget(self.value_label)
        
        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet("color: #cccccc; font-size: 16px; font-weight: 600;")
        value_layout.addWidget(self.unit_label)
        value_layout.addStretch()
        
        left.addLayout(value_layout)
        layout.addLayout(left, 1)

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
