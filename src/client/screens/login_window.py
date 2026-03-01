from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal
import requests


class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(int)
    show_registration_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("src/client/ui/login.ui", self)

        self.server_url = "http://localhost:5000"

        self.loginButton.clicked.connect(self.handle_login)
        self.registerButton.clicked.connect(self.show_registration_requested.emit)

    def handle_login(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите имя пользователя и пароль.")
            return

        try:
            response = requests.post(f"{self.server_url}/api/login",
                                     json={"username": username, "password": password},
                                     timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    user_id = data.get("user_id")
                    self.login_successful.emit(user_id)
            elif response.status_code == 401:
                QMessageBox.warning(self, "Ошибка входа", "Неверное имя пользователя или пароль.")
            else:
                QMessageBox.critical(self, "Ошибка сервера", f"Сервер вернул ошибку: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к серверу: {e}")
            QMessageBox.critical(self, "Ошибка подключения",
                                 "Не удалось подключиться к серверу.\n"
                                 "Убедитесь, что сервер запущен на http://localhost:5000")