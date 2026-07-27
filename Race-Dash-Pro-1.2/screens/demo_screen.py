from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt5.QtCore import Qt, QTimer
from widgets.tachometer import Tachometer
from widgets.gauge import Gauge
from widgets.sensor import Sensor
from rgb.rgb_controller import RGBController
from Logger import Logger

class DemoScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.rgb = RGBController(led_count=29, gpio_pin=18)
        self.logger = Logger()

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 8, 12, 8)

        tacho_layout = QHBoxLayout()
        tacho_layout.setAlignment(Qt.AlignCenter)
        
        self.tach = Tachometer()
        self.tach.setMinimumSize(280, 220)
        self.tach.setMaximumSize(380, 260)
        self.tach.setStyleSheet("background: #0a0c10; border: 2px solid #2a2e35; border-radius: 150px;")
        tacho_layout.addWidget(self.tach)
        layout.addLayout(tacho_layout)

        shift_layout = QHBoxLayout()
        shift_layout.setAlignment(Qt.AlignCenter)
        shift_layout.setSpacing(10)
        self.leds = []
        for color in ["#00ffcc", "#ffcc00", "#ff3366"]:
            led = QLabel()
            led.setFixedSize(70, 10)
            led.setStyleSheet(f"background-color: #1a1f2a; border-radius: 5px;")
            shift_layout.addWidget(led)
            self.leds.append(led)
        layout.addLayout(shift_layout)

        primary_layout = QHBoxLayout()
        primary_layout.setSpacing(15)

        self.boost_gauge = Gauge("BOOST", "bar", "#ffcc00", 2.5)
        self.oil_gauge = Gauge("OIL PRESS", "bar", "#00b4d8", 6)
        primary_layout.addWidget(self.boost_gauge)
        primary_layout.addWidget(self.oil_gauge)
        layout.addLayout(primary_layout)

        grid = QGridLayout()
        grid.setSpacing(6)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        sensors_data = [
            "BOOST", "COOLANT", "OIL TEMP", 
            "VOLTAGE", "EGT", "LAMBDA",
            "AFR", "FUEL PRESS", "INTAKE AIR",
            "FUEL TEMP", "AMBIENT", "TPS"
        ]

        units = {
            "BOOST": "bar", "COOLANT": "°C", "OIL TEMP": "°C",
            "VOLTAGE": "V", "EGT": "°C", "LAMBDA": "λ",
            "AFR": "AFR", "FUEL PRESS": "bar", "INTAKE AIR": "°C",
            "FUEL TEMP": "°C", "AMBIENT": "°C", "TPS": "%"
        }

        colors = {
            "BOOST": "#ffcc00", "COOLANT": "#00ffcc", "OIL TEMP": "#ff6600",
            "VOLTAGE": "#4CAF50", "EGT": "#ff8888", "LAMBDA": "#2ecc71",
            "AFR": "#e67e22", "FUEL PRESS": "#9b59b6", "INTAKE AIR": "#00b4d8",
            "FUEL TEMP": "#f4a261", "AMBIENT": "#88ddff", "TPS": "#ffcc88"
        }

        max_vals = {
            "BOOST": 2.5, "COOLANT": 130, "OIL TEMP": 150,
            "VOLTAGE": 16, "EGT": 1050, "LAMBDA": 1.2,
            "AFR": 18, "FUEL PRESS": 6, "INTAKE AIR": 50,
            "FUEL TEMP": 80, "AMBIENT": 40, "TPS": 100
        }

        self.sensors = {}
        row, col = 0, 0
        for label in sensors_data:
            unit = units.get(label, "")
            color = colors.get(label, "#ffffff")
            max_val = max_vals.get(label, 100)
            sensor = Sensor(label, unit, color, max_val)
            self.sensors[label] = sensor
            grid.addWidget(sensor, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.addLayout(grid)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_demo)
        self.timer.start(50)
        self.demo_time = 0

    def update_demo(self):
        self.demo_time += 0.02
        if self.demo_time > 10:
            self.demo_time = 0

        if self.demo_time < 3:
            rpm = 800 + self.demo_time * 2400
        elif self.demo_time < 6:
            rpm = 8000
        else:
            rpm = 8000 - (self.demo_time - 6) * 2400

        rpm = max(800, min(8000, rpm))
        load = rpm / 8000

        self.tach.set_value_animated(int(rpm / 80))
        self.rgb.set_shift_lights(rpm)

        if rpm > 7000:
            self.leds[0].setStyleSheet("background-color: #00ffcc; border-radius: 5px;")
            self.leds[1].setStyleSheet("background-color: #ffcc00; border-radius: 5px;")
            self.leds[2].setStyleSheet("background-color: #ff3366; border-radius: 5px;")
        elif rpm > 6000:
            self.leds[0].setStyleSheet("background-color: #00ffcc; border-radius: 5px;")
            self.leds[1].setStyleSheet("background-color: #ffcc00; border-radius: 5px;")
            self.leds[2].setStyleSheet("background-color: #1a1f2a; border-radius: 5px;")
        elif rpm > 5000:
            self.leds[0].setStyleSheet("background-color: #00ffcc; border-radius: 5px;")
            self.leds[1].setStyleSheet("background-color: #1a1f2a; border-radius: 5px;")
            self.leds[2].setStyleSheet("background-color: #1a1f2a; border-radius: 5px;")
        else:
            for led in self.leds:
                led.setStyleSheet("background-color: #1a1f2a; border-radius: 5px;")

        boost = load * 1.5
        oil_press = 1.2 + load * 4.3
        coolant = 85 + load * 40
        oil_temp = 90 + load * 50
        voltage = 14.2 - load * 0.8
        egt = 400 + load * 600
        lambda_val = 1.0 - load * 0.12
        afr = lambda_val * 14.7
        fuel_press = 3.8 + load * 1.5
        intake = 20 + load * 30
        fuel_temp = 30 + load * 25
        ambient = 20 + load * 15
        tps = load * 100

        self.boost_gauge.set_value_animated(boost)
        self.oil_gauge.set_value_animated(oil_press)

        self.sensors["BOOST"].set_value_animated(boost)
        self.sensors["COOLANT"].set_value_animated(coolant)
        self.sensors["OIL TEMP"].set_value_animated(oil_temp)
        self.sensors["VOLTAGE"].set_value_animated(voltage)
        self.sensors["EGT"].set_value_animated(egt)
        self.sensors["LAMBDA"].set_value_animated(lambda_val)
        self.sensors["AFR"].set_value_animated(afr)
        self.sensors["FUEL PRESS"].set_value_animated(fuel_press)
        self.sensors["INTAKE AIR"].set_value_animated(intake)
        self.sensors["FUEL TEMP"].set_value_animated(fuel_temp)
        self.sensors["AMBIENT"].set_value_animated(ambient)
        self.sensors["TPS"].set_value_animated(tps)

        log_data = {
            'rpm': rpm,
            'boost': boost,
            'coolant': coolant,
            'oil_temp': oil_temp,
            'voltage': voltage,
            'egt': egt,
            'lambda': lambda_val,
            'afr': afr,
            'fuel_press': fuel_press,
            'intake': intake,
            'fuel_temp': fuel_temp,
            'ambient': ambient,
            'tps': tps,
            'oil_press': oil_press
        }
        self.logger.log_data(log_data)
