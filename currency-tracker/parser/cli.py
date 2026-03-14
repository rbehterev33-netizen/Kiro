#!/usr/bin/env python3
"""
CLI интерфейс для Currency Tracker
"""

import sys
import json
from analyzer import CurrencyAnalyzer

def print_header(text):
    print("\n" + "="*50)
    print(text)
    print("="*50)

def cmd_trend(args):
    """Показать тренд валютной пары"""
    if len(args) < 1:
        print("Использование: trend <PAIR> [days]")
        print("Пример: trend USD/RUB 7")
        return
    
    pair = args[0]
    days = int(args[1]) if len(args) > 1 else 7
    
    base, target = pair.split('/')
    analyzer = CurrencyAnalyzer()
    
    trend = analyzer.get_trend_analysis(base, target, days)
    rsi = analyzer.get_rsi(base, target)
    predicted = analyzer.predict_rate(base, target, days)
    
    print_header(f"Анализ {pair}")
    print(f"Период: {days} дней")
    print(f"Тренд: {trend}")
    print(f"RSI: {rsi:.2f}" if rsi else "RSI: N/A")
    print(f"Прогноз: {predicted:.4f}" if predicted else "Прогноз: N/A")
    
    analyzer.close()

def cmd_arbitrage(args):
    """Поиск арбитражных возможностей"""
    analyzer = CurrencyAnalyzer()
    opportunities = analyzer.find_arbitrage()
    
    print_header("Арбитражные возможности")
    
    if not opportunities:
        print("Арбитражных возможностей не найдено")
    else:
        for opp in opportunities:
            print(f"{opp['currency_a']} → {opp['currency_b']} → {opp['currency_c']}: "
                  f"+{opp['profit_percent']:.4f}%")
    
    analyzer.close()

def cmd_volatility(args):
    """Рейтинг по волатильности"""
    days = int(args[0]) if args else 7
    
    analyzer = CurrencyAnalyzer()
    ranking = analyzer.get_volatility_ranking(days)
    
    print_header(f"Топ-10 волатильных пар ({days} дней)")
    
    for i, item in enumerate(ranking, 1):
        print(f"{i}. {item['currency_pair']}: "
              f"σ={item['volatility']:.4f}, avg={item['avg_rate']:.4f}")
    
    analyzer.close()

def cmd_report(args):
    """Генерация отчета"""
    if len(args) < 1:
        print("Использование: report <PAIR> [days]")
        return
    
    pair = args[0]
    days = int(args[1]) if len(args) > 1 else 30
    
    analyzer = CurrencyAnalyzer()
    report = analyzer.generate_report(pair, days)
    
    print_header(f"Отчет по {pair}")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    analyzer.close()

def cmd_alerts(args):
    """Проверка алертов"""
    analyzer = CurrencyAnalyzer()
    alerts = analyzer.check_alerts()
    
    print_header("Проверка алертов")
    
    if not alerts:
        print("Сработавших алертов нет")
    else:
        for alert in alerts:
            print(f"[{alert['alert_type']}] {alert['currency_pair']}: {alert['message']}")
    
    analyzer.close()

def cmd_help(args):
    """Показать справку"""
    print_header("Currency Tracker CLI")
    print("\nДоступные команды:")
    print("  trend <PAIR> [days]     - Анализ тренда")
    print("  arbitrage               - Поиск арбитража")
    print("  volatility [days]       - Рейтинг волатильности")
    print("  report <PAIR> [days]    - Генерация отчета")
    print("  alerts                  - Проверка алертов")
    print("  visualize <PAIR> [days] - Визуализация графика")
    print("  export <fmt> <PAIR> [d] - Экспорт данных (csv/json)")
    print("  help                    - Эта справка")
    print("\nПримеры:")
    print("  python cli.py trend USD/RUB 7")
    print("  python cli.py arbitrage")
    print("  python cli.py report EUR/RUB 30")
    print("  python cli.py visualize USD/RUB 30")
    print("  python cli.py export csv USD/RUB 30")

def cmd_visualize(args):
    """Визуализация данных"""
    if len(args) < 1:
        print("Использование: visualize <PAIR> [days]")
        return
    
    pair = args[0]
    days = int(args[1]) if len(args) > 1 else 30
    
    from visualizer import CurrencyVisualizer
    
    base, target = pair.split('/')
    viz = CurrencyVisualizer()
    viz.plot_rate_history(base, target, days)
    viz.close()

def cmd_export(args):
    """Экспорт данных"""
    if len(args) < 2:
        print("Использование: export <format> <PAIR> [days]")
        print("Форматы: csv, json")
        return
    
    format_type = args[0]
    pair = args[1]
    days = int(args[2]) if len(args) > 2 else 30
    
    from exporter import DataExporter
    
    base, target = pair.split('/')
    exporter = DataExporter()
    
    if format_type == 'csv':
        exporter.export_to_csv(base, target, days)
    elif format_type == 'json':
        exporter.export_to_json(base, target, days)
    else:
        print(f"Неизвестный формат: {format_type}")
    
    exporter.close()

def main():
    if len(sys.argv) < 2:
        cmd_help([])
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        'trend': cmd_trend,
        'arbitrage': cmd_arbitrage,
        'volatility': cmd_volatility,
        'report': cmd_report,
        'alerts': cmd_alerts,
        'visualize': cmd_visualize,
        'export': cmd_export,
        'help': cmd_help
    }
    
    if command in commands:
        try:
            commands[command](args)
        except Exception as e:
            print(f"Ошибка: {e}")
    else:
        print(f"Неизвестная команда: {command}")
        cmd_help([])

if __name__ == '__main__':
    main()
