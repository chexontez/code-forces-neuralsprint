import sys
import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.client.screens.login_window import LoginWindow
from src.client.screens.registration_window import RegistrationWindow
from src.client.screens.main_window import MainWindow
from src.database.database import DatabaseManager
from src.utils.pdf_generator import generate_pdf_report # <-- Импортируем генератор

class WindowManager:
    def __init__(self):
        self.current_user_id = None
        self.local_db_manager = DatabaseManager()
        self.app_icon = QIcon("assets/images/neuralsprint.png")

        self.login_window = LoginWindow(self.local_db_manager)
        self.login_window.setWindowIcon(self.app_icon)
        
        self.registration_window = RegistrationWindow()
        self.registration_window.setWindowIcon(self.app_icon)
        
        self.main_window = None

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
        self.main_window = MainWindow(user_id=self.current_user_id, db_manager=self.local_db_manager)
        self.main_window.setWindowIcon(self.app_icon)
        self.login_window.hide()
        self.main_window.show()
        
    def cleanup(self):
        """Выполняется перед закрытием: сохраняет отчет и закрывает БД."""
        if self.current_user_id:
            print("Создание автоматического PDF-отчета...")
            try:
                username = self.local_db_manager.get_username_by_id(self.current_user_id) or "unknown_user"
                results = self.local_db_manager.get_test_results(self.current_user_id)
                
                if results:
                    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filepath = f"pdf/log_{now}.pdf"
                    generate_pdf_report(username, results, filepath)
                    print(f"Отчет для {username} сохранен в {filepath}")
            except Exception as e:
                print(f"Не удалось создать PDF-отчет: {e}")

        self.local_db_manager.close()
        print("Соединение с локальной БД закрыто.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    manager = WindowManager()
    manager.show_login()
    
    exit_code = app.exec()
    manager.cleanup()
    sys.exit(exit_code)
