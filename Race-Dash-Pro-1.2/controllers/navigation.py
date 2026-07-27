from PyQt5.QtCore import QObject

class NavigationController(QObject):
    def __init__(self, swipe_container):
        super().__init__()
        self.swipe_container = swipe_container

    def go_to_demo(self):
        self.swipe_container.navigate_to(0)

    def go_to_logs(self):
        self.swipe_container.navigate_to(1)

    def go_to_graphs(self):
        self.swipe_container.navigate_to(2)
