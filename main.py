import sys
from PyQt6.QtWidgets import QApplication

from src.client.screens.login_window import LoginWindow
from src.client.screens.registration_window import RegistrationWindow
from src.client.screens.main_window import MainWindow
from src.database.database import DatabaseManager


class WindowManager:
    """Класс для управления окнами и общими ресурсами"""
    def __init__(self):
        self.current_user_id = None
        self.db_manager = DatabaseManager()  # <-- Единый экземпляр

        # Передаем менеджер в конструкторы
        self.login_window = LoginWindow(self.db_manager)
        self.registration_window = RegistrationWindow(self.db_manager)
        self.main_window = None

        # Настраиваем переходы
        self.login_window.show_registration_requested.connect(self.show_registration)
        self.login_window.login_successful.connect(self.show_main)
        
        self.registration_window.back_to_login_requested.connect(self.show_login)
        self.registration_window.registration_successful.connect(self.show_login)

    def show_login(self):
        if self.main_window: self.main_window.hide()
        self.registration_window.hide()
        self.login_window.show()

    def show_registration(self):
        self.login_window.hide()
        self.registration_window.show()

    def show_main(self, user_id):
        self.current_user_id = user_id
        # Теперь передаем и ID, и общий db_manager
        self.main_window = MainWindow(user_id=self.current_user_id, db_manager=self.db_manager)
        self.login_window.hide()
        self.main_window.show()
        
    def cleanup(self):
        """Закрывает все ресурсы перед выходом."""
        self.db_manager.close()
        print("Соединение с БД закрыто.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    manager = WindowManager()
    manager.show_login()
    
    exit_code = app.exec()
    manager.cleanup()
    sys.exit(exit_code)
