import psycopg2
import psycopg2.pool
from psycopg2.extras import execute_values, RealDictCursor
from config import DB_CONFIG
from datetime import datetime

# Пул соединений (инициализируется при первом использовании)
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)
    return _pool


class Database:
    def __init__(self, use_pool=False):
        self.conn = None
        self.cursor = None
        self._use_pool = use_pool

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        self.disconnect()

    def connect(self):
        """Подключение к базе данных"""
        try:
            if self._use_pool:
                self.conn = get_pool().getconn()
            else:
                self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def connect_dict(self):
        """Подключение с RealDictCursor (возвращает dict вместо tuple)"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Отключение от базы данных"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if self._use_pool:
                get_pool().putconn(self.conn)
            else:
                self.conn.close()

    def get_source_id(self, source_name):
        """Получить ID источника данных"""
        self.cursor.execute(
            "SELECT source_id FROM data_sources WHERE name = %s", (source_name,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def insert_rates(self, rates_data):
        """Вставка курсов валют"""
        query = """
            INSERT INTO exchange_rates
            (base_currency, target_currency, rate, rate_date, source_id)
            VALUES %s
            ON CONFLICT DO NOTHING
        """
        try:
            execute_values(self.cursor, query, rates_data)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка вставки данных: {e}")
            return 0

    def log_parsing(self, source_id, status, records_added, execution_time, error_msg=None):
        """Логирование парсинга"""
        try:
            self.cursor.execute(
                """INSERT INTO parsing_log
                   (source_id, parse_date, status, records_added, execution_time_ms, error_message)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (source_id, datetime.now().date(), status, records_added, execution_time, error_msg)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка логирования: {e}")
            self.conn.rollback()

    def get_currency_code(self, code):
        """Проверка существования валюты"""
        self.cursor.execute("SELECT code FROM currencies WHERE code = %s", (code,))
        return self.cursor.fetchone() is not None

    def fetchall_dict(self, query, params=None):
        """Выполнить запрос и вернуть список словарей"""
        self.cursor.execute(query, params)
        cols = [desc[0] for desc in self.cursor.description]
        return [dict(zip(cols, row)) for row in self.cursor.fetchall()]

    def fetchone_dict(self, query, params=None):
        """Выполнить запрос и вернуть один словарь"""
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        if row is None:
            return None
        cols = [desc[0] for desc in self.cursor.description]
        return dict(zip(cols, row))
