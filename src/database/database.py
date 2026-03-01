import sqlite3
import hashlib
import datetime

class DatabaseManager:
    def __init__(self, db_name="neuralsprint.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS test_results (id INTEGER PRIMARY KEY, user_id INTEGER, test_date TEXT, avg_reaction_time REAL, missed_go INTEGER, false_alarms INTEGER, FOREIGN KEY (user_id) REFERENCES users (id))")
        self.conn.commit()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_user(self, username, password):
        password_hash = self._hash_password(password)
        self.cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def cache_user(self, username, password, user_id):
        password_hash = self._hash_password(password)
        self.cursor.execute("REPLACE INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, username, password_hash))
        self.conn.commit()

    def get_username_by_id(self, user_id):
        self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_test_result(self, user_id, results):
        date = datetime.datetime.now().isoformat()
        avg_rt = sum(results['reaction_times']) / len(results['reaction_times']) if results['reaction_times'] else 0
        self.cursor.execute("INSERT INTO test_results (user_id, test_date, avg_reaction_time, missed_go, false_alarms) VALUES (?, ?, ?, ?, ?)", (user_id, date, avg_rt, results['missed_go'], results['false_alarms']))
        self.conn.commit()

    def get_test_results(self, user_id):
        self.cursor.execute("SELECT test_date, avg_reaction_time, missed_go, false_alarms FROM test_results WHERE user_id = ? ORDER BY test_date DESC", (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
