import sys
from PyQt6.QtWidgets import QApplication

from src.client.screens.login_window import LoginWindow
from src.client.screens.registration_window import RegistrationWindow
from src.client.screens.main_window import MainWindow


class WindowManager:
    """Класс для управления окнами"""
    def __init__(self):
        self.current_user_id = None
        
        self.login_window = LoginWindow()
        self.registration_window = RegistrationWindow()
        # MainWindow теперь создается при необходимости
        self.main_window = None

        # Настраиваем переходы
        self.login_window.show_registration_requested.connect(self.show_registration)
        self.login_window.login_successful.connect(self.show_main)
        
        self.registration_window.back_to_login_requested.connect(self.show_login)
        self.registration_window.registration_successful.connect(self.show_login)

    def show_login(self):
        if self.main_window:
            self.main_window.hide()
        self.registration_window.hide()
        self.login_window.show()

    def show_registration(self):
        self.login_window.hide()
        self.registration_window.show()

    def show_main(self, user_id):
        self.current_user_id = user_id
        print(f"Пользователь {self.current_user_id} вошел в систему.")
        
        # Создаем MainWindow с ID пользователя
        self.main_window = MainWindow(user_id=self.current_user_id)
        self.login_window.hide()
        self.main_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    manager = WindowManager()
    manager.show_login()
    sys.exit(app.exec())
