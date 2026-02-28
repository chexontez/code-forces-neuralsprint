from PyQt6.QtWidgets import QWidget, QTableWidgetItem
from PyQt6.uic import loadUi
import datetime

from src.database.database import DatabaseManager


class StatisticsWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        loadUi("src/client/ui/statistics_window.ui", self)

        self.user_id = user_id
        self.db_manager = DatabaseManager()

        self.closeButton.clicked.connect(self.close)
        self.load_statistics()

    def load_statistics(self):
        """Загружает и отображает статистику в таблице."""
        results = self.db_manager.get_test_results(self.user_id)
        self.resultsTable.setRowCount(len(results))

        for row_num, row_data in enumerate(results):
            # Форматируем дату для лучшей читаемости
            date_str = datetime.datetime.fromisoformat(row_data[0]).strftime('%Y-%m-%d %H:%M')
            
            self.resultsTable.setItem(row_num, 0, QTableWidgetItem(date_str))
            self.resultsTable.setItem(row_num, 1, QTableWidgetItem(f"{row_data[1]:.2f}"))
            self.resultsTable.setItem(row_num, 2, QTableWidgetItem(str(row_data[2])))
            self.resultsTable.setItem(row_num, 3, QTableWidgetItem(str(row_data[3])))
            
    def closeEvent(self, event):
        self.db_manager.close()
        super().closeEvent(event)
