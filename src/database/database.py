import sqlite3
import hashlib
import datetime
import json
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_name="neuralsprint.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.db_name = db_name
        # ===== НОВОЕ: Добавляем поддержку офлайн режима =====
        self.is_online = True
        self.offline_cache_path = Path.home() / '.neuralsprint' / 'offline_cache.json'
        self.offline_cache_path.parent.mkdir(parents=True, exist_ok=True)
        # =====================================================
        self.setup_database()

    def setup_database(self):
        """Создает таблицы, если они не существуют."""
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                username
                                TEXT
                                UNIQUE
                                NOT
                                NULL,
                                password_hash
                                TEXT
                                NOT
                                NULL
                            )
                            """)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS test_results
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                user_id
                                INTEGER
                                NOT
                                NULL,
                                test_date
                                TEXT
                                NOT
                                NULL,
                                avg_reaction_time
                                REAL,
                                missed_go
                                INTEGER,
                                false_alarms
                                INTEGER,
                                FOREIGN
                                KEY
                            (
                                user_id
                            ) REFERENCES users
                            (
                                id
                            )
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

        try:
            self.cursor.execute("""
                                INSERT INTO test_results (user_id, test_date, avg_reaction_time, missed_go, false_alarms)
                                VALUES (?, ?, ?, ?, ?)
                                """, (user_id, date, avg_rt, results['missed_go'], results['false_alarms']))
            self.conn.commit()
            print(f"Результат для пользователя {user_id} сохранен.")

            # ===== НОВОЕ: Кэшируем результат для офлайн режима =====
            self._cache_test_result(user_id, date, avg_rt, results['missed_go'], results['false_alarms'])
            # ========================================================
        except Exception as e:
            print(f"Ошибка при сохранении результата: {e}")

    def get_test_results(self, user_id):
        """Возвращает историю тестов для указанного пользователя."""
        try:
            self.cursor.execute("""
                                SELECT test_date, avg_reaction_time, missed_go, false_alarms
                                FROM test_results
                                WHERE user_id = ?
                                ORDER BY test_date DESC
                                """, (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении результатов: {e}")
            # ===== НОВОЕ: В офлайн режиме загружаем кэш =====
            return self._load_cached_results(user_id)
            # ==================================================

    # ===== НОВОЕ: Методы для кэширования результатов в офлайн режиме =====
    def _cache_test_result(self, user_id, date, avg_rt, missed_go, false_alarms):
        """Кэширует результат теста локально"""
        try:
            cache = {}
            if self.offline_cache_path.exists():
                with open(self.offline_cache_path, 'r') as f:
                    cache = json.load(f)

            user_key = str(user_id)
            if user_key not in cache:
                cache[user_key] = []

            cache[user_key].append({
                'test_date': date,
                'avg_reaction_time': avg_rt,
                'missed_go': missed_go,
                'false_alarms': false_alarms
            })

            with open(self.offline_cache_path, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            print(f"Ошибка при кэшировании: {e}")

    def _load_cached_results(self, user_id):
        """Загружает кэшированные результаты тестов"""
        try:
            if self.offline_cache_path.exists():
                with open(self.offline_cache_path, 'r') as f:
                    cache = json.load(f)
                    user_key = str(user_id)
                    if user_key in cache:
                        results = cache[user_key]
                        # Преобразуем в формат как в БД (кортежи)
                        return [(r['test_date'], r['avg_reaction_time'], r['missed_go'], r['false_alarms'])
                                for r in sorted(results, key=lambda x: x['test_date'], reverse=True)]
        except Exception as e:
            print(f"Ошибка при загрузке кэша: {e}")
        return []

    # ====================================================================

    def close(self):
        """Закрывает соединение с БД."""
        self.conn.close()