from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent

from src.core.engine import TestEngine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("src/client/ui/main_window.ui", self)

        self.test_engine = TestEngine()

        # Подключаем сигналы к слотам
        self.test_engine.color_changed.connect(self.update_stimulus)
        self.test_engine.test_finished.connect(self.show_results)
        self.test_engine.test_started.connect(self.on_test_start)

        # Подключаем меню
        self.actionAbout.triggered.connect(self.show_about_dialog)
        self.actionStatistics.triggered.connect(self.show_statistics_placeholder)

        # Устанавливаем обработчик клика для stimulusFrame
        self.stimulusFrame.mousePressEvent = self.handle_stimulus_click
        
        # Инициализируем начальное состояние
        self.update_stimulus("white")

    def keyPressEvent(self, event: QKeyEvent):
        """Обрабатывает нажатия клавиш."""
        if event.key() == Qt.Key.Key_Escape and self.test_engine.is_running:
            self.test_engine.stop_test()

    def on_test_start(self):
        """Вызывается при старте теста."""
        self.update_stimulus("red")

    def update_stimulus(self, color):
        """Обновляет цвет фона и текст области стимула."""
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
        """Обрабатывает клик по области стимула."""
        if not self.test_engine.is_running:
            self.test_engine.start_test()
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.test_engine.record_reaction()

    def show_results(self, results):
        """Отображает результаты теста."""
        self.update_stimulus("white")
        
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
        """Показывает диалоговое окно "О приложении"."""
        QMessageBox.about(self, "О приложении",
                          "NeuroSprint - тренажер для развития скорости реакции.\n\n"
                          "Версия 1.0")

    def show_statistics_placeholder(self):
        """Заглушка для окна статистики."""
        QMessageBox.information(self, "Статистика", "Этот раздел находится в разработке.")

