#!/usr/bin/env python3
"""
Currency Tracker Parser
Парсер курсов валют с различных источников
"""

import time
from datetime import datetime
from database import Database
from parsers import CBRParser, ECBParser, MOEXParser, CryptoParser
from config import SOURCES


def _ensure_source(db, name, url, description=""):
    """Добавить источник в БД если его нет"""
    db.cursor.execute("SELECT source_id FROM data_sources WHERE name = %s", (name,))
    row = db.cursor.fetchone()
    if row:
        return row[0]
    db.cursor.execute(
        "INSERT INTO data_sources (name, url, description) VALUES (%s, %s, %s) RETURNING source_id",
        (name, url, description)
    )
    db.conn.commit()
    return db.cursor.fetchone()[0]


def _ensure_currency(db, code, name, symbol=""):
    """Добавить валюту в БД если её нет"""
    db.cursor.execute("SELECT code FROM currencies WHERE code = %s", (code,))
    if not db.cursor.fetchone():
        try:
            db.cursor.execute(
                "INSERT INTO currencies (code, name, symbol) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (code, name, symbol)
            )
            db.conn.commit()
        except Exception:
            db.conn.rollback()


def parse_source(source_key, source_config, db):
    """Парсинг данных из источника"""
    start_time = time.time()
    source_name = source_config['name']

    print(f"\n{'='*50}")
    print(f"Парсинг: {source_name}")
    print(f"{'='*50}")

    source_id = _ensure_source(db, source_name, source_config['url'])

    try:
        if source_key == 'cbr':
            parser = CBRParser(source_config['url'])
            xml_data = parser.fetch()
            rates = parser.parse(xml_data)

        elif source_key == 'ecb':
            parser = ECBParser(source_config['url'])
            xml_data = parser.fetch()
            rates = parser.parse(xml_data)

        elif source_key == 'moex':
            parser = MOEXParser()
            data = parser.fetch()
            rates = parser.parse(data)

        elif source_key == 'crypto':
            parser = CryptoParser()
            data = parser.fetch()
            rates = parser.parse(data)
            # Убедимся что крипто-валюты есть в справочнике
            crypto_names = {
                "BTC": ("Bitcoin", "₿"),
                "ETH": ("Ethereum", "Ξ"),
                "USDT": ("Tether", "₮"),
                "BNB": ("BNB", ""),
                "SOL": ("Solana", ""),
                "XRP": ("XRP", ""),
                "TON": ("Toncoin", ""),
            }
            for code, (name, symbol) in crypto_names.items():
                _ensure_currency(db, code, name, symbol)

        else:
            print(f"Неизвестный источник: {source_key}")
            return

        print(f"Получено курсов: {len(rates)}")

        rates_data = []
        for rate in rates:
            if not db.get_currency_code(rate['base_currency']):
                print(f"  Пропуск: {rate['base_currency']} не в справочнике")
                continue
            if not db.get_currency_code(rate['target_currency']):
                print(f"  Пропуск: {rate['target_currency']} не в справочнике")
                continue
            rates_data.append((
                rate['base_currency'],
                rate['target_currency'],
                rate['rate'],
                rate['rate_date'],
                source_id
            ))

        records_added = db.insert_rates(rates_data)
        execution_time = int((time.time() - start_time) * 1000)
        db.log_parsing(source_id, 'success', records_added, execution_time)
        print(f"✓ Сохранено записей: {records_added}  ({execution_time} мс)")

    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        db.log_parsing(source_id, 'failed', 0, execution_time, str(e))
        print(f"✗ Ошибка: {e}")


def main():
    print("\n" + "="*50)
    print("Currency Tracker Parser")
    print(f"Запуск: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    db = Database()
    if not db.connect():
        print("Не удалось подключиться к БД")
        return

    print("✓ Подключение к БД установлено")

    for source_key, source_config in SOURCES.items():
        if source_config.get('enabled', False):
            parse_source(source_key, source_config, db)
        else:
            print(f"\nИсточник '{source_config['name']}' отключен")

    db.disconnect()
    print("\n" + "="*50)
    print("Парсинг завершен")
    print("="*50 + "\n")


if __name__ == '__main__':
    main()
