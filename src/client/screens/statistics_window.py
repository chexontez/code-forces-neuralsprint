from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt6.uic import loadUi
import datetime

from src.database.database import DatabaseManager
from src.utils.pdf_generator import generate_pdf_report


class StatisticsWindow(QDialog):
    def __init__(self, user_id, db_manager: DatabaseManager, parent=None):
        super().__init__(parent) # <-- Устанавливаем родителя
        loadUi("src/client/ui/statistics_window.ui", self)

        self.user_id = user_id
        self.db_manager = db_manager
        self.results = []

        self.closeButton.clicked.connect(self.accept) # Для QDialog лучше использовать accept/reject
        self.exportPdfButton.clicked.connect(self.export_to_pdf)
        self.load_statistics()

    def load_statistics(self):
        """Загружает и отображает статистику в таблице."""
        self.results = self.db_manager.get_test_results(self.user_id)
        self.resultsTable.setRowCount(len(self.results))

        for row_num, row_data in enumerate(self.results):
            date_str = datetime.datetime.fromisoformat(row_data[0]).strftime('%Y-%m-%d %H:%M')
            
            self.resultsTable.setItem(row_num, 0, QTableWidgetItem(date_str))
            self.resultsTable.setItem(row_num, 1, QTableWidgetItem(f"{row_data[1]:.2f}"))
            self.resultsTable.setItem(row_num, 2, QTableWidgetItem(str(row_data[2])))
            self.resultsTable.setItem(row_num, 3, QTableWidgetItem(str(row_data[3])))
            
    def export_to_pdf(self):
        """Открывает диалог сохранения и генерирует PDF."""
        username_cursor = self.db_manager.cursor.execute("SELECT username FROM users WHERE id = ?", (self.user_id,))
        username = username_cursor.fetchone()[0] or "Unknown"

        filepath, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", f"{username}_report.pdf", "PDF Files (*.pdf)")

        if filepath:
            try:
                generate_pdf_report(username, self.results, filepath)
                QMessageBox.information(self, "Успех", f"Отчет успешно сохранен в {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчет:\n{e}")
                print(e)
