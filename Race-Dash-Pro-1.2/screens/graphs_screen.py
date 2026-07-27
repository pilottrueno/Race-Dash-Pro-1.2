from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
import random
from widgets.graph_widget import GraphWidget

class GraphsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 10, 15, 10)

        # Заголовок + выбор датчика
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)
        top_layout.setSpacing(15)

        title = QLabel("📊 ГРАФИКИ")
        title.setStyleSheet("color: #00b4d8; font-size: 22px; font-weight: bold;")
        top_layout.addWidget(title)

        self.sensor_combo = QComboBox()
        self.sensor_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e2f;
                color: #ccc;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 6px 15px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e2f;
                color: #ccc;
                selection-background-color: #2a2e35;
            }
        """)
        self.sensor_combo.addItems([
            "RPM", "BOOST", "COOLANT", "OIL TEMP",
            "VOLTAGE", "EGT", "LAMBDA", "AFR",
            "FUEL PRESS", "INTAKE AIR", "FUEL TEMP", "AMBIENT", "TPS"
        ])
        self.sensor_combo.currentTextChanged.connect(self.change_sensor)
        top_layout.addWidget(self.sensor_combo)

        layout.addLayout(top_layout)

        # ГРАФИК
        self.graph = GraphWidget()
        self.graph.setMinimumHeight(300)
        layout.addWidget(self.graph, 1)

        # Информационная строка
        info_layout = QHBoxLayout()
        info_layout.setAlignment(Qt.AlignCenter)
        info_layout.setSpacing(20)

        self.info_label = QLabel("📈 Обновление каждые 1.5 сек")
        self.info_label.setStyleSheet("color: #8a8f99; font-size: 12px;")
        info_layout.addWidget(self.info_label)

        refresh_btn = QPushButton("🔄 ОБНОВИТЬ")
        refresh_btn.setStyleSheet("background: #1a1f2a; border: 1px solid #00b4d8; color: #00b4d8; border-radius: 30px; padding: 6px 16px; font-weight: bold; font-size: 10px;")
        refresh_btn.clicked.connect(self.generate_new_data)
        info_layout.addWidget(refresh_btn)

        layout.addLayout(info_layout)

        # Таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_new_data)
        self.timer.start(1500)

        self.generate_new_data()

    def generate_new_data(self):
        import random
        data = [random.randint(0, 100) for _ in range(80)]
        self.graph.set_data(data)
        
        sensor = self.sensor_combo.currentText()
        last_val = data[-1] if data else 0
        from datetime import datetime
        self.info_label.setText(f"📊 {sensor} | Последнее: {last_val} | {datetime.now().strftime('%H:%M:%S')}")

    def change_sensor(self, sensor):
        colors = {
            "RPM": "#ff3366",
            "BOOST": "#ffcc00",
            "COOLANT": "#00ffcc",
            "OIL TEMP": "#ff6600",
            "VOLTAGE": "#4CAF50",
            "EGT": "#ff8888",
            "LAMBDA": "#2ecc71",
            "AFR": "#e67e22",
            "FUEL PRESS": "#9b59b6",
            "INTAKE AIR": "#00b4d8",
            "FUEL TEMP": "#f4a261",
            "AMBIENT": "#88ddff",
            "TPS": "#ffcc88"
        }
        color = colors.get(sensor, "#00b4d8")
        self.graph.color = QColor(color)
        self.generate_new_data()
