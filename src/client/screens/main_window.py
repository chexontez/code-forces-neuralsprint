from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent
import requests

from src.core.engine import TestEngine
from src.database.database import DatabaseManager
from src.client.screens.statistics_window import StatisticsWindow

class MainWindow(QMainWindow):
    def __init__(self, user_id, db_manager: DatabaseManager):
        super().__init__()
        loadUi("src/client/ui/main_window.ui", self)

        self.user_id = user_id
        self.db_manager = db_manager
        self.test_engine = TestEngine()
        self.server_url = "http://localhost:5000"
        
        self.test_engine.color_changed.connect(self.update_stimulus)
        self.test_engine.test_finished.connect(self.process_results) # <-- Изменено
        self.test_engine.test_started.connect(self.on_test_start)

        self.actionAbout.triggered.connect(self.show_about_dialog)
        self.actionStatistics.triggered.connect(self.show_statistics)

        self.stimulusFrame.mousePressEvent = self.handle_stimulus_click
        self.update_stimulus("white")

    def process_results(self, results):
        """Обрабатывает результаты: сохраняет локально, отправляет на сервер, отображает."""
        # 1. Всегда сохраняем локально
        self.db_manager.add_test_result(self.user_id, results)
        print("Результат сохранен локально.")

        # 2. Пытаемся отправить на сервер
        try:
            payload = {"user_id": self.user_id, "results": results}
            response = requests.post(f"{self.server_url}/api/save_result", json=payload, timeout=3)
            if response.status_code == 200:
                print("Результат успешно отправлен на сервер.")
            else:
                print(f"Сервер вернул ошибку при сохранении: {response.status_code}")
        except requests.exceptions.RequestException:
            print("Не удалось отправить результат на сервер (сервер недоступен).")

        # 3. Отображаем пользователю
        self.show_results_text(results)

    def show_results_text(self, results):
        self.update_stimulus("white")
        text = "Тест завершен!\n"
        avg_rt = sum(results['reaction_times']) / len(results['reaction_times']) if results['reaction_times'] else 0
        text += f"Среднее время реакции: {avg_rt:.2f} мс\n"
        text += f"Пропущено Go-стимулов: {results['missed_go']}\n"
        text += f"Ложных нажатий на No-Go: {results['false_alarms']}\n"
        self.resultsTextEdit.setText(text)

    # ... (остальной код без изменений) ...
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape and self.test_engine.is_running:
            self.test_engine.stop_test()
    def on_test_start(self): self.update_stimulus("red")
    def update_stimulus(self, color):
        text_color = "white";
        if color == "white": self.infoLabel.setText("Начать тест"); text_color = "black"
        elif color == "red": self.infoLabel.setText("Приготовьтесь")
        if color == "green": self.infoLabel.hide()
        else: self.infoLabel.show()
        self.stimulusFrame.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        self.infoLabel.setStyleSheet(f"color: {text_color};")
    def handle_stimulus_click(self, event: QMouseEvent):
        if not self.test_engine.is_running: self.test_engine.start_test()
        elif event.button() == Qt.MouseButton.LeftButton: self.test_engine.record_reaction()
    def show_about_dialog(self): QMessageBox.about(self, "О приложении", "    NeuroSprint...    \n\nВерсия 1.0\n")
    def show_statistics(self):
        dialog = StatisticsWindow(self.user_id, self.db_manager, self)
        dialog.exec()
