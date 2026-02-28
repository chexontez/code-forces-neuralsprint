from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent

from src.core.engine import TestEngine
from src.database.database import DatabaseManager
from src.client.screens.statistics_window import StatisticsWindow


class MainWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        loadUi("src/client/ui/main_window.ui", self)

        self.user_id = user_id
        self.test_engine = TestEngine()
        self.db_manager = DatabaseManager()
        self.statistics_window = None # Для хранения экземпляра окна

        # Подключаем сигналы к слотам
        self.test_engine.color_changed.connect(self.update_stimulus)
        self.test_engine.test_finished.connect(self.save_and_show_results)
        self.test_engine.test_started.connect(self.on_test_start)

        # Подключаем меню
        self.actionAbout.triggered.connect(self.show_about_dialog)
        self.actionStatistics.triggered.connect(self.show_statistics)

        # Устанавливаем обработчик клика
        self.stimulusFrame.mousePressEvent = self.handle_stimulus_click
        self.update_stimulus("white")

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape and self.test_engine.is_running:
            self.test_engine.stop_test()

    def on_test_start(self):
        self.update_stimulus("red")

    def update_stimulus(self, color):
        text_color = "white"
        if color == "white":
            self.infoLabel.setText("Начать тест")
            text_color = "black"
        elif color == "red":
            self.infoLabel.setText("Приготовьтесь")
        
        if color == "green":
            self.infoLabel.hide()
        else:
            self.infoLabel.show()
            
        self.stimulusFrame.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        self.infoLabel.setStyleSheet(f"color: {text_color};")

    def handle_stimulus_click(self, event: QMouseEvent):
        if not self.test_engine.is_running:
            self.test_engine.start_test()
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.test_engine.record_reaction()

    def save_and_show_results(self, results):
        """Сохраняет результаты в БД и отображает их."""
        self.update_stimulus("white")
        
        if self.user_id is not None:
            self.db_manager.add_test_result(self.user_id, results)

        text = "Тест завершен!\n"
        if results['reaction_times']:
            avg_rt = sum(results['reaction_times']) / len(results['reaction_times'])
            text += f"Среднее время реакции: {avg_rt:.2f} мс\n"
        else:
            text += "Среднее время реакции: N/A\n"
        text += f"Пропущено Go-стимулов: {results['missed_go']}\n"
        text += f"Ложных нажатий на No-Go: {results['false_alarms']}\n"
        self.resultsTextEdit.setText(text)

    def show_about_dialog(self):
        QMessageBox.about(self, "О приложении", "NeuroSprint v1.0")

    def show_statistics(self):
        """Открывает окно статистики."""
        # Создаем окно только если оно еще не открыто
        if self.statistics_window is None or not self.statistics_window.isVisible():
            self.statistics_window = StatisticsWindow(self.user_id)
            self.statistics_window.show()
        
    def closeEvent(self, event):
        self.db_manager.close()
        # Закрываем и окно статистики, если оно есть
        if self.statistics_window:
            self.statistics_window.close()
        super().closeEvent(event)
