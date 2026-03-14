#!/usr/bin/env python3
"""
Планировщик задач для Currency Tracker
"""

import schedule
import time
from datetime import datetime
from main import main as parse_main
from analyzer import CurrencyAnalyzer

def job_parse():
    """Задача парсинга"""
    print(f"\n[{datetime.now()}] Запуск парсинга...")
    parse_main()

def job_check_alerts():
    """Задача проверки алертов"""
    print(f"\n[{datetime.now()}] Проверка алертов...")
    analyzer = CurrencyAnalyzer()
    alerts = analyzer.check_alerts()
    
    if alerts:
        print(f"Сработало алертов: {len(alerts)}")
        for alert in alerts:
            print(f"  [{alert['alert_type']}] {alert['currency_pair']}: {alert['message']}")
    else:
        print("Алертов нет")
    
    analyzer.close()

def job_calculate_statistics():
    """Задача расчета статистики"""
    print(f"\n[{datetime.now()}] Расчет статистики...")
    from database import Database
    
    db = Database()
    db.connect()
    
    # Расчет статистики за неделю для всех пар
    query = """
        SELECT DISTINCT base_currency || '/' || target_currency AS pair
        FROM exchange_rates
        WHERE rate_date >= CURRENT_DATE - 7
    """
    db.cursor.execute(query)
    pairs = db.cursor.fetchall()
    
    for pair in pairs:
        try:
            db.cursor.execute(
                "SELECT calculate_currency_statistics(%s, CURRENT_DATE - 6, CURRENT_DATE)",
                (pair[0],)
            )
            db.conn.commit()
        except Exception as e:
            print(f"Ошибка расчета статистики для {pair[0]}: {e}")
    
    print(f"Статистика рассчитана для {len(pairs)} пар")
    db.disconnect()

def main():
    """Главная функция планировщика"""
    print("="*50)
    print("Currency Tracker Scheduler")
    print("="*50)
    
    # Парсинг каждый день в 9:00
    schedule.every().day.at("09:00").do(job_parse)
    
    # Проверка алертов каждый час
    schedule.every().hour.do(job_check_alerts)
    
    # Расчет статистики каждый день в 23:00
    schedule.every().day.at("23:00").do(job_calculate_statistics)
    
    print("\nЗапланированные задачи:")
    print("  - Парсинг: ежедневно в 9:00")
    print("  - Проверка алертов: каждый час")
    print("  - Расчет статистики: ежедневно в 23:00")
    print("\nПланировщик запущен. Нажмите Ctrl+C для остановки.\n")
    
    # Запуск планировщика
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПланировщик остановлен")
