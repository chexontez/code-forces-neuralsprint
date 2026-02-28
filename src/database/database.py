import sqlite3
import hashlib
import datetime


class DatabaseManager:
    def __init__(self, db_name="neuralsprint.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        """Создает таблицы, если они не существуют."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_date TEXT NOT NULL,
                avg_reaction_time REAL,
                missed_go INTEGER,
                false_alarms INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        self.conn.commit()

    def _hash_password(self, password):
        """Хэширует пароль."""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password):
        """Добавляет нового пользователя. Возвращает True/False."""
        if not username or not password:
            return False
        password_hash = self._hash_password(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                              (username, password_hash))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def check_user(self, username, password):
        """Проверяет учетные данные. Возвращает user_id или None."""
        password_hash = self._hash_password(password)
        self.cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        if result and result[1] == password_hash:
            return result[0]  # Возвращаем user_id
        return None

    def add_test_result(self, user_id, results):
        """Добавляет результат теста в БД."""
        date = datetime.datetime.now().isoformat()
        avg_rt = sum(results['reaction_times']) / len(results['reaction_times']) if results['reaction_times'] else 0
        
        self.cursor.execute("""
            INSERT INTO test_results (user_id, test_date, avg_reaction_time, missed_go, false_alarms)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, date, avg_rt, results['missed_go'], results['false_alarms']))
        self.conn.commit()
        print(f"Результат для пользователя {user_id} сохранен.")

    def get_test_results(self, user_id):
        """Возвращает историю тестов для указанного пользователя."""
        self.cursor.execute("""
            SELECT test_date, avg_reaction_time, missed_go, false_alarms 
            FROM test_results 
            WHERE user_id = ? 
            ORDER BY test_date DESC
        """, (user_id,))
        return self.cursor.fetchall()

    def close(self):
        """Закрывает соединение с БД."""
        self.conn.close()
