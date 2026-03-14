#!/usr/bin/env python3
"""
Тестовый скрипт для проверки структуры проекта
Работает без подключения к БД
"""

import os
import sys

def check_file(path, description):
    """Проверка наличия файла"""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def check_directory(path, description):
    """Проверка наличия директории"""
    exists = os.path.isdir(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def main():
    print("="*60)
    print("Currency Tracker - Проверка структуры проекта")
    print("="*60)
    print()
    
    # Проверка документации
    print("📄 Документация:")
    check_file("README.md", "README")
    check_file("QUICKSTART.md", "Быстрый старт")
    check_file("EXAMPLES.md", "Примеры")
    check_file("CHANGELOG.md", "История изменений")
    check_file("LICENSE", "Лицензия EN")
    check_file("LICENSE_RU", "Лицензия RU")
    check_file(".gitignore", "Git ignore")
    print()
    
    # Проверка SQL скриптов
    print("🗄️  SQL скрипты:")
    scripts_dir = "scripts"
    if check_directory(scripts_dir, "Директория скриптов"):
        sql_files = [
            "00_create_database.sql",
            "01_create_tables.sql",
            "02_add_constraints.sql",
            "03_create_indexes.sql",
            "04_create_triggers.sql",
            "05_insert_test_data.sql",
            "06_create_views.sql",
            "07_useful_queries.sql",
            "08_create_functions.sql",
            "09_create_alerts.sql"
        ]
        for sql_file in sql_files:
            check_file(os.path.join(scripts_dir, sql_file), f"  {sql_file}")
        
        check_file(os.path.join(scripts_dir, "deploy.sh"), "  deploy.sh")
        check_file(os.path.join(scripts_dir, "deploy.bat"), "  deploy.bat")
    print()
    
    # Проверка Python модулей
    print("🐍 Python модули:")
    parser_dir = "parser"
    if check_directory(parser_dir, "Директория парсера"):
        python_files = [
            "main.py",
            "config.py",
            "database.py",
            "analyzer.py",
            "visualizer.py",
            "exporter.py",
            "api_server.py",
            "scheduler.py",
            "cli.py",
            "requirements.txt",
            ".env.example"
        ]
        for py_file in python_files:
            check_file(os.path.join(parser_dir, py_file), f"  {py_file}")
        
        # Проверка парсеров
        parsers_dir = os.path.join(parser_dir, "parsers")
        if check_directory(parsers_dir, "  Директория парсеров"):
            check_file(os.path.join(parsers_dir, "__init__.py"), "    __init__.py")
            check_file(os.path.join(parsers_dir, "cbr_parser.py"), "    cbr_parser.py")
            check_file(os.path.join(parsers_dir, "ecb_parser.py"), "    ecb_parser.py")
    print()
    
    # Подсчет статистики
    print("📊 Статистика проекта:")
    
    total_files = 0
    total_lines = 0
    
    # SQL файлы
    sql_count = 0
    sql_lines = 0
    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith('.sql'):
                sql_count += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        sql_lines += len(f.readlines())
                except:
                    pass
    
    # Python файлы
    py_count = 0
    py_lines = 0
    for root, dirs, files in os.walk(parser_dir):
        for file in files:
            if file.endswith('.py'):
                py_count += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        py_lines += len(f.readlines())
                except:
                    pass
    
    # Документация
    doc_count = 0
    doc_lines = 0
    for file in ['README.md', 'QUICKSTART.md', 'EXAMPLES.md', 'CHANGELOG.md']:
        if os.path.exists(file):
            doc_count += 1
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    doc_lines += len(f.readlines())
            except:
                pass
    
    print(f"  SQL файлов: {sql_count} ({sql_lines} строк)")
    print(f"  Python файлов: {py_count} ({py_lines} строк)")
    print(f"  Документация: {doc_count} файлов ({doc_lines} строк)")
    print(f"  Всего строк кода: {sql_lines + py_lines + doc_lines}")
    print()
    
    # Возможности проекта
    print("🚀 Возможности проекта:")
    features = [
        "Парсинг курсов валют (ЦБ РФ, ЕЦБ)",
        "Хранение исторических данных",
        "Анализ трендов и волатильности",
        "Расчет технических индикаторов (RSI, SMA)",
        "Прогнозирование курсов",
        "Поиск арбитражных возможностей",
        "Система алертов и уведомлений",
        "Визуализация данных",
        "Экспорт в CSV/JSON",
        "REST API",
        "CLI интерфейс",
        "Планировщик задач"
    ]
    for feature in features:
        print(f"  ✓ {feature}")
    print()
    
    print("="*60)
    print("Проверка завершена!")
    print("="*60)
    print()
    print("📝 Следующие шаги:")
    print("  1. Установите PostgreSQL")
    print("  2. Запустите: cd scripts && deploy.bat (или deploy.sh)")
    print("  3. Установите зависимости: cd parser && pip install -r requirements.txt")
    print("  4. Настройте .env файл")
    print("  5. Запустите парсер: python main.py")
    print()

if __name__ == '__main__':
    main()
