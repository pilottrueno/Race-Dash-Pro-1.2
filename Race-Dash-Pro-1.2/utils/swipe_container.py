from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QVariantAnimation

class SwipeContainer(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked = stacked_widget
        self._start_pos = None
        self._press_time = 0
        self._initial_x = 0
        self._swipe_threshold = 100

        self._animation = QPropertyAnimation(self.stacked, b'pos')
        self._animation.setDuration(350)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._animation.finished.connect(self._on_animation_finished)

        self._velocity_anim = QVariantAnimation()
        self._velocity_anim.setDuration(400)
        self._velocity_anim.setEasingCurve(QEasingCurve.OutQuad)
        self._velocity_anim.valueChanged.connect(lambda v: self.stacked.move(v, 0))
        self._velocity_anim.finished.connect(self._finish_inertia)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.pos()
            self._press_time = event.timestamp()
            self._initial_x = self.stacked.x()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._start_pos is None:
            return
        delta = event.pos() - self._start_pos
        new_x = self._initial_x + delta.x()
        self.stacked.move(new_x, 0)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._start_pos is None or event.button() != Qt.LeftButton:
            super().mouseReleaseEvent(event)
            return

        delta = event.pos() - self._start_pos
        abs_dx = abs(delta.x())
        current_x = self.stacked.x()

        elapsed = max(event.timestamp() - self._press_time, 1)
        speed = delta.x() / (elapsed / 1000.0)

        if abs_dx < self._swipe_threshold and abs(speed) < 50:
            self._animate_to(0, 0)
            self._start_pos = None
            super().mouseReleaseEvent(event)
            return

        current_index = self.stacked.currentIndex()
        total = self.stacked.count()
        if delta.x() > 0:
            next_index = (current_index - 1) % total
        else:
            next_index = (current_index + 1) % total

        if abs_dx > self._swipe_threshold or abs(speed) > 150:
            self.stacked.setCurrentIndex(next_index)
            self._velocity_anim.setStartValue(current_x)
            self._velocity_anim.setEndValue(0)
            self._velocity_anim.start()
        else:
            self.stacked.setCurrentIndex(next_index)
            self._animate_to(0, 0)

        self._start_pos = None
        super().mouseReleaseEvent(event)

    def _animate_to(self, x, y):
        self._animation.stop()
        self._animation.setStartValue(self.stacked.pos())
        self._animation.setEndValue(QPoint(x, y))
        self._animation.start()

    def _on_animation_finished(self):
        self.stacked.move(0, 0)

    def _finish_inertia(self):
        self.stacked.move(0, 0)

    def navigate_to(self, index):
        current = self.stacked.currentIndex()
        if current == index:
            return
        self.stacked.setCurrentIndex(index)
        self._animate_to(0, 0)
