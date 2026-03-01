import sqlite3
import hashlib
import datetime

class ServerDatabaseManager:
    def __init__(self, db_name="server.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS test_results (id INTEGER PRIMARY KEY, user_id INTEGER, test_date TEXT, avg_reaction_time REAL, missed_go INTEGER, false_alarms INTEGER, variability REAL, accuracy REAL, FOREIGN KEY (user_id) REFERENCES users (id))")
        self.conn.commit()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password):
        try:
            self.cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, self._hash_password(password)))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user_by_id(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def get_user_by_username(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute("SELECT id, username FROM users ORDER BY username")
        return self.cursor.fetchall()

    def get_test_results(self, user_id):
        self.cursor.execute("SELECT *, strftime('%Y-%m-%d %H:%M', test_date) as date FROM test_results WHERE user_id = ? ORDER BY test_date DESC", (user_id,))
        return self.cursor.fetchall()

    def add_test_result(self, user_id, results):
        """Добавляет результат теста в серверную БД."""
        date = datetime.datetime.now().isoformat()
        avg_rt = sum(results.get('reaction_times', [])) / len(results.get('reaction_times', [1]))
        self.cursor.execute("""
            INSERT INTO test_results (user_id, test_date, avg_reaction_time, missed_go, false_alarms)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, date, avg_rt, results.get('missed_go', 0), results.get('false_alarms', 0)))
        self.conn.commit()

    def close(self):
        self.conn.close()
