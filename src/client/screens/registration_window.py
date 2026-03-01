from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal
import requests

class RegistrationWindow(QMainWindow):
    back_to_login_requested = pyqtSignal()
    registration_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("src/client/ui/registration.ui", self)
        
        self.server_url = "http://localhost:5000"

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

        try:
            response = requests.post(f"{self.server_url}/register", 
                                     json={"username": username, "password": password},
                                     timeout=5)
            
            if response.status_code == 201: # Created
                QMessageBox.information(self, "Успех", "Регистрация прошла успешно! Теперь вы можете войти.")
                self.registration_successful.emit()
            elif response.status_code == 409: # Conflict
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует.")
            else:
                QMessageBox.critical(self, "Ошибка сервера", f"Сервер вернул ошибку: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к серверу: {e}")
            QMessageBox.critical(self, "Ошибка подключения", 
                                 "Не удалось подключиться к серверу.\n"
                                 "Убедитесь, что сервер запущен.")
