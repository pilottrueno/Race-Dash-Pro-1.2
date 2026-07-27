from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtProperty, QPropertyAnimation, QEasingCurve, QPoint, QSize
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont

class Tachometer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._last_pos = None
        self._is_dragging = False
        self.min_value = 0
        self.max_value = 100
        self.start_angle = 135
        self.span_angle = 270

        self.animation = QPropertyAnimation(self, b'value')
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.setMinimumSize(300, 240)
        self.setMaximumSize(400, 280)

    @pyqtProperty(int)
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if v != self._value:
            self._value = max(self.min_value, min(self.max_value, v))
            self.update()

    def set_value_animated(self, new_value):
        self.animation.stop()
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(new_value)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        center = rect.center()
        radius = int(min(rect.width(), rect.height()) / 2 - 20)

        painter.save()
        painter.translate(center)
        painter.rotate(-self.start_angle)

        pen = QPen(QColor("#8a8f99"))
        pen.setWidth(3)
        painter.setPen(pen)

        steps = 11
        for i in range(steps):
            angle = i * (self.span_angle / (steps - 1))
            painter.save()
            painter.rotate(angle)
            painter.drawLine(radius - 25, 0, radius, 0)
            painter.restore()

        painter.restore()

        painter.save()
        painter.translate(center)
        norm = (self._value - self.min_value) / (self.max_value - self.min_value)
        angle = self.start_angle + norm * self.span_angle
        painter.rotate(angle)

        arrow_points = [QPoint(0, -15), QPoint(-8, 30), QPoint(8, 30)]
        painter.setBrush(QBrush(QColor("#ff3366")))
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawPolygon(arrow_points)
        painter.restore()

        painter.setFont(QFont("Arial", 22, QFont.Bold))
        painter.setPen(QColor("#00ffcc"))
        painter.drawText(rect, Qt.AlignCenter, f"{self._value}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().manhattanLength() < 100:
            self._is_dragging = True
            self._last_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_dragging and self._last_pos is not None:
            delta = event.pos() - self._last_pos
            self.value += delta.x() * 0.2
            self._last_pos = event.pos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._is_dragging:
            self._is_dragging = False
            self._last_pos = None
        super().mouseReleaseEvent(event)

    def sizeHint(self):
        return QSize(300, 240)

    def minimumSizeHint(self):
        return QSize(300, 240)
