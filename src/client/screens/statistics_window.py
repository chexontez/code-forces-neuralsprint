from PyQt6.QtWidgets import QDialog, QTableWidgetItem
from PyQt6.uic import loadUi
import datetime

from src.database.database import DatabaseManager


class StatisticsWindow(QDialog):
    def __init__(self, user_id, db_manager: DatabaseManager, parent=None):
        super().__init__(parent) # <-- Устанавливаем родителя
        loadUi("src/client/ui/statistics_window.ui", self)

        self.user_id = user_id
        self.db_manager = db_manager

        self.closeButton.clicked.connect(self.accept) # Для QDialog лучше использовать accept/reject
        self.load_statistics()

    def load_statistics(self):
        """Загружает и отображает статистику в таблице."""
        results = self.db_manager.get_test_results(self.user_id)
        self.resultsTable.setRowCount(len(results))

        for row_num, row_data in enumerate(results):
            date_str = datetime.datetime.fromisoformat(row_data[0]).strftime('%Y-%m-%d %H:%M')
            
            self.resultsTable.setItem(row_num, 0, QTableWidgetItem(date_str))
            self.resultsTable.setItem(row_num, 1, QTableWidgetItem(f"{row_data[1]:.2f}")) # avg_rt
            self.resultsTable.setItem(row_num, 2, QTableWidgetItem(f"{row_data[4]:.2f}")) # variability
            self.resultsTable.setItem(row_num, 3, QTableWidgetItem(f"{row_data[5]:.2f}")) # accuracy
            self.resultsTable.setItem(row_num, 4, QTableWidgetItem(str(row_data[2])))      # missed_go
            self.resultsTable.setItem(row_num, 5, QTableWidgetItem(str(row_data[3])))      # false_alarms
