#!/usr/bin/env python3
"""
Демонстрация функциональности без подключения к БД
Использует тестовые данные
"""

from datetime import datetime, timedelta
import random

class MockData:
    """Генератор тестовых данных"""
    
    @staticmethod
    def generate_rates(base, target, days=30):
        """Генерация тестовых курсов"""
        rates = []
        base_rate = 92.5 if target == 'RUB' else 0.92
        
        for i in range(days):
            date = datetime.now().date() - timedelta(days=days-i-1)
            # Добавляем случайное изменение
            rate = base_rate + random.uniform(-2, 2)
            rates.append({
                'date': date,
                'rate': round(rate, 4)
            })
            base_rate = rate
        
        return rates

def demo_trend_analysis():
    """Демонстрация анализа тренда"""
    print("\n" + "="*60)
    print("📈 Анализ тренда USD/RUB")
    print("="*60)
    
    rates = MockData.generate_rates('USD', 'RUB', 7)
    
    print("\nКурсы за последние 7 дней:")
    for item in rates:
        print(f"  {item['date']}: {item['rate']:.4f}")
    
    # Определение тренда
    first_rate = rates[0]['rate']
    last_rate = rates[-1]['rate']
    change_percent = ((last_rate - first_rate) / first_rate) * 100
    
    if change_percent > 1:
        trend = "📈 Восходящий тренд (uptrend)"
    elif change_percent < -1:
        trend = "📉 Нисходящий тренд (downtrend)"
    else:
        trend = "➡️  Стабильный (stable)"
    
    print(f"\nТренд: {trend}")
    print(f"Изменение: {change_percent:+.2f}%")
    print(f"Первый курс: {first_rate:.4f}")
    print(f"Последний курс: {last_rate:.4f}")

def demo_rsi_calculation():
    """Демонстрация расчета RSI"""
    print("\n" + "="*60)
    print("📊 Расчет RSI индикатора")
    print("="*60)
    
    rates = MockData.generate_rates('USD', 'EUR', 14)
    
    # Упрощенный расчет RSI
    gains = []
    losses = []
    
    for i in range(1, len(rates)):
        change = rates[i]['rate'] - rates[i-1]['rate']
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    print(f"\nRSI (14 периодов): {rsi:.2f}")
    
    if rsi > 70:
        print("Сигнал: Перекупленность (overbought)")
    elif rsi < 30:
        print("Сигнал: Перепроданность (oversold)")
    else:
        print("Сигнал: Нейтральная зона")

def demo_volatility():
    """Демонстрация расчета волатильности"""
    print("\n" + "="*60)
    print("📉 Анализ волатильности")
    print("="*60)
    
    pairs = [
        ('USD', 'RUB'),
        ('EUR', 'RUB'),
        ('GBP', 'RUB'),
        ('CNY', 'RUB')
    ]
    
    print("\nРейтинг волатильности (7 дней):")
    
    volatilities = []
    for base, target in pairs:
        rates = MockData.generate_rates(base, target, 7)
        values = [r['rate'] for r in rates]
        
        # Расчет стандартного отклонения
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        volatilities.append({
            'pair': f"{base}/{target}",
            'volatility': std_dev,
            'avg_rate': mean
        })
    
    volatilities.sort(key=lambda x: x['volatility'], reverse=True)
    
    for i, item in enumerate(volatilities, 1):
        print(f"  {i}. {item['pair']}: σ={item['volatility']:.4f}, "
              f"avg={item['avg_rate']:.4f}")

def demo_prediction():
    """Демонстрация прогнозирования"""
    print("\n" + "="*60)
    print("🔮 Прогнозирование курса (SMA)")
    print("="*60)
    
    rates = MockData.generate_rates('EUR', 'RUB', 7)
    
    print("\nИсторические данные:")
    for item in rates[-5:]:
        print(f"  {item['date']}: {item['rate']:.4f}")
    
    # Простое скользящее среднее
    values = [r['rate'] for r in rates]
    sma = sum(values) / len(values)
    
    print(f"\nПрогноз (SMA-7): {sma:.4f}")
    print(f"Текущий курс: {rates[-1]['rate']:.4f}")
    print(f"Разница: {(sma - rates[-1]['rate']):.4f}")

def demo_arbitrage():
    """Демонстрация поиска арбитража"""
    print("\n" + "="*60)
    print("💱 Поиск арбитражных возможностей")
    print("="*60)
    
    # Тестовые курсы
    rates = {
        ('USD', 'EUR'): 0.92,
        ('EUR', 'GBP'): 0.86,
        ('GBP', 'USD'): 1.27
    }
    
    print("\nТекущие курсы:")
    for (base, target), rate in rates.items():
        print(f"  {base}/{target}: {rate:.4f}")
    
    # Проверка треугольного арбитража
    usd_to_eur = rates[('USD', 'EUR')]
    eur_to_gbp = rates[('EUR', 'GBP')]
    gbp_to_usd = rates[('GBP', 'USD')]
    
    result = usd_to_eur * eur_to_gbp * gbp_to_usd
    profit = (result - 1) * 100
    
    print(f"\nТреугольный арбитраж USD → EUR → GBP → USD:")
    print(f"  Результат: {result:.6f}")
    print(f"  Прибыль: {profit:+.4f}%")
    
    if profit > 0.1:
        print("  ✓ Арбитражная возможность найдена!")
    else:
        print("  ✗ Арбитраж невыгоден")

def demo_alerts():
    """Демонстрация системы алертов"""
    print("\n" + "="*60)
    print("🔔 Система алертов")
    print("="*60)
    
    # Тестовые алерты
    alerts = [
        {
            'pair': 'USD/RUB',
            'type': 'price',
            'threshold': 95.00,
            'condition': 'above',
            'current': 96.50
        },
        {
            'pair': 'EUR/RUB',
            'type': 'change_percent',
            'threshold': 2.00,
            'condition': 'above',
            'current': 2.5
        }
    ]
    
    print("\nНастроенные алерты:")
    for alert in alerts:
        print(f"\n  Пара: {alert['pair']}")
        print(f"  Тип: {alert['type']}")
        print(f"  Порог: {alert['threshold']}")
        print(f"  Условие: {alert['condition']}")
        print(f"  Текущее значение: {alert['current']}")
        
        if alert['type'] == 'price':
            if alert['condition'] == 'above' and alert['current'] > alert['threshold']:
                print(f"  🔔 АЛЕРТ! Курс превысил {alert['threshold']}")
        elif alert['type'] == 'change_percent':
            if alert['current'] > alert['threshold']:
                print(f"  🔔 АЛЕРТ! Изменение {alert['current']}% превысило порог")

def demo_export():
    """Демонстрация экспорта данных"""
    print("\n" + "="*60)
    print("📤 Экспорт данных")
    print("="*60)
    
    rates = MockData.generate_rates('USD', 'RUB', 7)
    
    # Экспорт в CSV формат (демонстрация)
    print("\nПример CSV экспорта:")
    print("Date,Rate,Change,Change %")
    for i, item in enumerate(rates):
        if i > 0:
            change = item['rate'] - rates[i-1]['rate']
            change_pct = (change / rates[i-1]['rate']) * 100
            print(f"{item['date']},{item['rate']:.4f},{change:.4f},{change_pct:.2f}")
        else:
            print(f"{item['date']},{item['rate']:.4f},,")
    
    # Экспорт в JSON формат (демонстрация)
    print("\nПример JSON экспорта:")
    print("{")
    print('  "currency_pair": "USD/RUB",')
    print('  "period_days": 7,')
    print('  "data": [')
    for i, item in enumerate(rates[:3]):
        comma = "," if i < 2 else ""
        print(f'    {{"date": "{item["date"]}", "rate": {item["rate"]:.4f}}}{comma}')
    print('    ...')
    print('  ]')
    print("}")

def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("Currency Tracker - Демонстрация функциональности")
    print("(Работает без подключения к БД)")
    print("="*60)
    
    demos = [
        ("Анализ тренда", demo_trend_analysis),
        ("Расчет RSI", demo_rsi_calculation),
        ("Волатильность", demo_volatility),
        ("Прогнозирование", demo_prediction),
        ("Поиск арбитража", demo_arbitrage),
        ("Система алертов", demo_alerts),
        ("Экспорт данных", demo_export)
    ]
    
    for name, func in demos:
        try:
            func()
        except Exception as e:
            print(f"\nОшибка в {name}: {e}")
    
    print("\n" + "="*60)
    print("Демонстрация завершена!")
    print("="*60)
    print("\n📝 Для полноценной работы:")
    print("  1. Установите PostgreSQL")
    print("  2. Разверните БД: cd scripts && deploy.bat")
    print("  3. Установите зависимости: pip install -r parser/requirements.txt")
    print("  4. Запустите парсер: python parser/main.py")
    print()

if __name__ == '__main__':
    main()
