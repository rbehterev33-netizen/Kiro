#!/usr/bin/env python3
"""
Currency Tracker Parser
Парсер курсов валют с различных источников
"""

import time
from datetime import datetime
from database import Database
from parsers import CBRParser, ECBParser
from config import SOURCES

def parse_source(source_key, source_config, db):
    """Парсинг данных из источника"""
    start_time = time.time()
    source_name = source_config['name']
    
    print(f"\n{'='*50}")
    print(f"Парсинг: {source_name}")
    print(f"{'='*50}")
    
    # Получаем ID источника
    source_id = db.get_source_id(source_name)
    if not source_id:
        print(f"Ошибка: источник '{source_name}' не найден в БД")
        return
    
    try:
        # Выбираем парсер
        if source_key == 'cbr':
            parser = CBRParser(source_config['url'])
        elif source_key == 'ecb':
            parser = ECBParser(source_config['url'])
        else:
            print(f"Неизвестный источник: {source_key}")
            return
        
        # Получаем данные
        print("Загрузка данных...")
        xml_data = parser.fetch()
        
        # Парсим данные
        print("Парсинг данных...")
        rates = parser.parse(xml_data)
        print(f"Получено курсов: {len(rates)}")
        
        # Подготовка данных для вставки
        rates_data = []
        for rate in rates:
            # Проверяем существование валют
            if not db.get_currency_code(rate['base_currency']):
                print(f"Предупреждение: валюта {rate['base_currency']} не найдена в БД")
                continue
            if not db.get_currency_code(rate['target_currency']):
                print(f"Предупреждение: валюта {rate['target_currency']} не найдена в БД")
                continue
            
            rates_data.append((
                rate['base_currency'],
                rate['target_currency'],
                rate['rate'],
                rate['rate_date'],
                source_id
            ))
        
        # Вставка в БД
        print("Сохранение в БД...")
        records_added = db.insert_rates(rates_data)
        
        # Время выполнения
        execution_time = int((time.time() - start_time) * 1000)
        
        # Логирование
        db.log_parsing(source_id, 'success', records_added, execution_time)
        
        print(f"✓ Успешно добавлено записей: {records_added}")
        print(f"Время выполнения: {execution_time} мс")
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        db.log_parsing(source_id, 'failed', 0, execution_time, str(e))
        print(f"✗ Ошибка: {e}")

def main():
    """Основная функция"""
    print("\n" + "="*50)
    print("Currency Tracker Parser")
    print(f"Запуск: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # Подключение к БД
    db = Database()
    if not db.connect():
        print("Не удалось подключиться к БД")
        return
    
    print("✓ Подключение к БД установлено")
    
    # Парсинг всех активных источников
    for source_key, source_config in SOURCES.items():
        if source_config.get('enabled', False):
            parse_source(source_key, source_config, db)
        else:
            print(f"\nИсточник '{source_config['name']}' отключен")
    
    # Отключение от БД
    db.disconnect()
    
    print("\n" + "="*50)
    print("Парсинг завершен")
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
