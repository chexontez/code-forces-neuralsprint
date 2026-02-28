import sys
from PyQt6.QtWidgets import QApplication

from src.client.screens.login_window import LoginWindow
from src.client.screens.registration_window import RegistrationWindow
from src.client.screens.main_window import MainWindow


class WindowManager:
    """Класс для управления окнами"""
    def __init__(self):
        self.login_window = LoginWindow()
        self.registration_window = RegistrationWindow()
        self.main_window = MainWindow()

        # Настраиваем переходы между окнами через сигналы
        self.login_window.show_registration_requested.connect(self.show_registration)
        self.login_window.login_successful.connect(self.show_main)
        
        self.registration_window.back_to_login_requested.connect(self.show_login)
        self.registration_window.registration_successful.connect(self.show_login)

    def show_login(self):
        self.registration_window.hide()
        self.main_window.hide()
        self.login_window.show()

    def show_registration(self):
        self.login_window.hide()
        self.registration_window.show()

    def show_main(self):
        self.login_window.hide()
        self.main_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    manager = WindowManager()
    manager.show_login()
    sys.exit(app.exec())
