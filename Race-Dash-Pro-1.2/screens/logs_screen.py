from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import os
import subprocess
from datetime import datetime

class LogsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📄 ЛОГИ")
        title.setStyleSheet("color: #ff9900; font-size: 32px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        self.log_list = QListWidget()
        self.log_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2f;
                border: 1px solid #444;
                border-radius: 12px;
                padding: 10px;
                color: #ccc;
                font-size: 14px;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:hover {
                background-color: #2a2e35;
            }
        """)
        # Двойной клик для открытия файла
        self.log_list.itemDoubleClicked.connect(self.open_log_file)
        layout.addWidget(self.log_list)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(15)

        clear_btn = QPushButton("🗑️ ОЧИСТИТЬ")
        clear_btn.setStyleSheet("background: #1a1f2a; border: 1px solid #ff3366; color: #ff3366; border-radius: 30px; padding: 8px 20px; font-weight: bold; font-size: 11px;")
        clear_btn.clicked.connect(self.clear_logs)
        btn_layout.addWidget(clear_btn)

        export_btn = QPushButton("💾 ЭКСПОРТ ВСЕ")
        export_btn.setStyleSheet("background: #1a1f2a; border: 1px solid #4CAF50; color: #4CAF50; border-radius: 30px; padding: 8px 20px; font-weight: bold; font-size: 11px;")
        export_btn.clicked.connect(self.export_all_logs)
        btn_layout.addWidget(export_btn)

        refresh_btn = QPushButton("🔄 ОБНОВИТЬ")
        refresh_btn.setStyleSheet("background: #1a1f2a; border: 1px solid #00b4d8; color: #00b4d8; border-radius: 30px; padding: 8px 20px; font-weight: bold; font-size: 11px;")
        refresh_btn.clicked.connect(self.load_logs)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

        # Информация
        self.info_label = QLabel("💡 Двойной клик по файлу — открыть")
        self.info_label.setStyleSheet("color: #8a8f99; font-size: 12px;")
        layout.addWidget(self.info_label, alignment=Qt.AlignCenter)

        # Автообновление
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_logs)
        self.timer.start(5000)
        
        self.load_logs()

    def load_logs(self):
        """Загрузка списка логов"""
        self.log_list.clear()
        log_dir = "/home/pi/Race-Dash-Pro-1.1/logs"
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            self.log_list.addItem("📁 Папка logs создана")
            return
        
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.txt')]
        
        if not log_files:
            self.log_list.addItem("📭 Нет сохранённых логов")
            return
        
        for f in sorted(log_files, reverse=True):
            filepath = os.path.join(log_dir, f)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%H:%M:%S")
            item = QListWidgetItem(f"📄 {f} — {size} байт ({mtime})")
            item.setData(Qt.UserRole, filepath)  # Сохраняем полный путь
            self.log_list.addItem(item)

    def open_log_file(self, item):
        """Открыть файл двойным кликом"""
        filepath = item.data(Qt.UserRole)
        if not filepath or not os.path.exists(filepath):
            QMessageBox.warning(self, "Ошибка", f"Файл не найден:\n{filepath}")
            return
        
        try:
            # Открываем в текстовом редакторе по умолчанию
            if os.name == 'posix':  # Linux
                subprocess.Popen(['xdg-open', filepath])
            else:  # Windows
                os.startfile(filepath)
        except Exception as e:
            # Если не получилось — показываем содержимое в диалоге
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Ограничиваем размер для отображения
                if len(content) > 10000:
                    content = content[:10000] + "\n... (файл обрезан, показано 10000 символов)"
                
                msg = QMessageBox(self)
                msg.setWindowTitle(f"📄 {os.path.basename(filepath)}")
                msg.setText(content)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            except Exception as e2:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{str(e2)}")

    def clear_logs(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить все логи?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            log_dir = "/home/pi/Race-Dash-Pro-1.1/logs"
            for f in os.listdir(log_dir):
                if f.endswith('.txt'):
                    os.remove(os.path.join(log_dir, f))
            self.load_logs()
            QMessageBox.information(self, "Готово", "Логи очищены")

    def export_all_logs(self):
        """Экспорт всех логов в один файл"""
        log_dir = "/home/pi/Race-Dash-Pro-1.1/logs"
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.txt')]
        
        if not log_files:
            QMessageBox.warning(self, "Внимание", "Нет логов для экспорта")
            return

        filename = f"/home/pi/Race-Dash-Pro-1.1/logs/export_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as out:
                out.write("=== RACE DASH PRO — ВСЕ ЛОГИ ===\n")
                out.write(f"Экспорт: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                out.write("=" * 50 + "\n\n")
                
                for f in sorted(log_files):
                    filepath = os.path.join(log_dir, f)
                    out.write(f"\n--- {f} ---\n")
                    with open(filepath, 'r', encoding='utf-8') as inf:
                        out.write(inf.read())
                    out.write("\n" + "-" * 50 + "\n")
            
            QMessageBox.information(self, "Готово", f"Все логи объединены в:\n{filename}")
            self.load_logs()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать логи:\n{str(e)}")
