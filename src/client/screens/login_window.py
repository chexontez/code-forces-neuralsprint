from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal
import requests

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(int)
    show_registration_requested = pyqtSignal()

    def __init__(self, db_manager): # Снова принимаем db_manager
        super().__init__()
        loadUi("src/client/ui/login.ui", self)
        
        self.server_url = "http://localhost:5000"
        self.db_manager = db_manager # Сохраняем менеджер локальной БД

        self.loginButton.clicked.connect(self.handle_login)
        self.registerButton.clicked.connect(self.show_registration_requested.emit)

    def handle_login(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()

        try:
            # 1. Пытаемся войти через сервер
            response = requests.post(f"{self.server_url}/api/login", json={"username": username, "password": password}, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    user_id = data.get("user_id")
                    # Кэшируем успешный вход в локальную БД
                    self.db_manager.cache_user(username, password, user_id)
                    self.login_successful.emit(user_id)
                    return
        except requests.exceptions.RequestException:
            # 2. Если сервер недоступен, показываем предупреждение и пытаемся войти оффлайн
            QMessageBox.warning(self, "Оффлайн-режим", "Сервер недоступен. Попытка входа в оффлайн-режиме.")
        
        # 3. Пытаемся войти через локальную БД
        user_id = self.db_manager.check_user(username, password)
        if user_id:
            self.login_successful.emit(user_id)
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неверное имя пользователя или пароль (проверено оффлайн).")
