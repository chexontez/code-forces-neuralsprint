from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal

from src.database.database import DatabaseManager


class LoginWindow(QMainWindow):
    # Сигналы для переключения окон
    login_successful = pyqtSignal()
    show_registration_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("src/client/ui/login.ui", self)
        self.db_manager = DatabaseManager()

        self.loginButton.clicked.connect(self.handle_login)
        self.registerButton.clicked.connect(self.show_registration_requested.emit)

    def handle_login(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()

        if self.db_manager.check_user(username, password):
            self.login_successful.emit()
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неверное имя пользователя или пароль.")

    def closeEvent(self, event):
        self.db_manager.close()
        super().closeEvent(event)
