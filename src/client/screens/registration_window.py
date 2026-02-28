from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal

from src.database.database import DatabaseManager


class RegistrationWindow(QMainWindow):
    back_to_login_requested = pyqtSignal()
    registration_successful = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        loadUi("src/client/ui/registration.ui", self)
        self.db_manager = db_manager

        self.registerButton.clicked.connect(self.handle_registration)
        self.backButton.clicked.connect(self.back_to_login_requested.emit)

    def handle_registration(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        confirm_password = self.confirmPasswordLineEdit.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя и пароль не могут быть пустыми.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return

        if self.db_manager.add_user(username, password):
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно! Теперь вы можете войти.")
            self.registration_successful.emit()
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует.")
