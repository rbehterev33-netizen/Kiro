import psycopg2
from psycopg2.extras import execute_values
from config import DB_CONFIG
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False
    
    def disconnect(self):
        """Отключение от базы данных"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def get_source_id(self, source_name):
        """Получить ID источника данных"""
        query = "SELECT source_id FROM data_sources WHERE name = %s"
        self.cursor.execute(query, (source_name,))
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
        query = """
            INSERT INTO parsing_log 
            (source_id, parse_date, status, records_added, execution_time_ms, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (
                source_id,
                datetime.now().date(),
                status,
                records_added,
                execution_time,
                error_msg
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка логирования: {e}")
            self.conn.rollback()
    
    def get_currency_code(self, code):
        """Проверка существования валюты"""
        query = "SELECT code FROM currencies WHERE code = %s"
        self.cursor.execute(query, (code,))
        return self.cursor.fetchone() is not None
