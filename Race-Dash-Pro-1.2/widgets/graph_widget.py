from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QLinearGradient

class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.max_points = 100
        self.min_val = 0
        self.max_val = 100
        self.color = QColor("#00b4d8")
        self.setMinimumHeight(350)
        self.setStyleSheet("background-color: #0d1117; border: 1px solid #2a2e35; border-radius: 12px;")
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.add_random_data)
        self.timer.start(100)
    
    def add_data(self, value):
        self.data.append(value)
        if len(self.data) > self.max_points:
            self.data.pop(0)
        self.update()
    
    def add_random_data(self):
        import random
        value = random.randint(0, 100)
        self.add_data(value)
    
    def set_data(self, data_list):
        self.data = data_list[-self.max_points:]
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        margin = 20
        
        # Фон
        painter.fillRect(0, 0, w, h, QColor("#0d1117"))
        
        if len(self.data) < 2:
            painter.setPen(QColor("#8a8f99"))
            painter.drawText(w//2 - 50, h//2, "Нет данных")
            return
        
        # Сетка
        painter.setPen(QPen(QColor("#1a1f2a"), 1))
        for i in range(margin, w, 50):
            painter.drawLine(i, margin, i, h - margin)
        for i in range(margin, h - margin, 40):
            painter.drawLine(margin, i, w - margin, i)
        
        # Находим min/max
        min_val = min(self.data)
        max_val = max(self.data)
        if max_val - min_val < 1:
            max_val = min_val + 10
        range_val = max_val - min_val
        
        # Рисуем линию графика
        path = QPainterPath()
        step = (w - 2 * margin) / len(self.data)
        
        for i, val in enumerate(self.data):
            x = margin + i * step
            y = margin + (h - 2 * margin) - ((val - min_val) / range_val) * (h - 2 * margin)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        # Тень под графиком (градиент)
        gradient = QLinearGradient(0, margin, 0, h - margin)
        gradient.setColorAt(0, QColor(self.color).lighter(160))
        gradient.setColorAt(1, QColor("#0d1117"))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        path2 = QPainterPath(path)
        path2.lineTo(w - margin, h - margin)
        path2.lineTo(margin, h - margin)
        path2.closeSubpath()
        painter.drawPath(path2)
        
        # Основная линия
        painter.setPen(QPen(self.color, 3))
        painter.drawPath(path)
        
        # Точки на графике
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color, 1))
        for i, val in enumerate(self.data):
            x = margin + i * step
            y = margin + (h - 2 * margin) - ((val - min_val) / range_val) * (h - 2 * margin)
            painter.drawEllipse(QPoint(int(x), int(y)), 3, 3)
        
        # Последнее значение (крупно)
        if self.data:
            last_val = self.data[-1]
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.setFont(self.font())
            painter.drawText(10, 30, f"Последнее: {last_val}")
