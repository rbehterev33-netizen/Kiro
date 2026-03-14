# 📚 Примеры использования

## SQL запросы

### Базовые запросы

```sql
-- Последние курсы всех валют
SELECT * FROM v_latest_rates;

-- Курс USD/RUB за последнюю неделю
SELECT rate_date, rate 
FROM exchange_rates
WHERE base_currency = 'USD' AND target_currency = 'RUB'
  AND rate_date >= CURRENT_DATE - 7
ORDER BY rate_date DESC;

-- Статистика за месяц
SELECT * FROM v_monthly_statistics 
WHERE currency_pair = 'USD/RUB';
```

### Аналитические запросы

```sql
-- Конвертация валют
SELECT convert_currency(100, 'USD', 'RUB');

-- Прогноз курса на основе SMA
SELECT predict_rate_sma('USD', 'RUB', 7);

-- Определение тренда
SELECT get_trend('EUR', 'RUB', 14);

-- Расчет RSI
SELECT calculate_rsi('USD', 'EUR', 14);

-- Поиск арбитража
SELECT * FROM find_arbitrage_opportunities(CURRENT_DATE);
```

### Работа с алертами

```sql
-- Создание алерта
INSERT INTO currency_alerts (currency_pair, alert_type, threshold_value, condition)
VALUES ('USD/RUB', 'price', 95.00, 'above');

-- Проверка алертов
SELECT * FROM check_alerts();

-- История срабатывания
SELECT * FROM alert_history 
ORDER BY triggered_at DESC 
LIMIT 10;
```

## Python CLI

### Анализ данных

```bash
# Анализ тренда USD/RUB за 7 дней
python cli.py trend USD/RUB 7

# Генерация полного отчета
python cli.py report EUR/RUB 30

# Рейтинг волатильности
python cli.py volatility 14
```

### Поиск возможностей

```bash
# Поиск арбитражных возможностей
python cli.py arbitrage

# Проверка алертов
python cli.py alerts
```

### Визуализация

```bash
# График курса USD/RUB за месяц
python cli.py visualize USD/RUB 30

# Сравнение нескольких пар
python visualizer.py --compare USD/RUB EUR/RUB GBP/RUB --days 30
```

### Экспорт данных

```bash
# Экспорт в CSV
python cli.py export csv USD/RUB 30

# Экспорт в JSON
python cli.py export json EUR/RUB 30

# Экспорт статистики
python exporter.py --statistics --format json
```

## REST API

### Получение данных

```bash
# Последние курсы
curl http://localhost:5000/api/rates/latest

# История курса USD/RUB за 30 дней
curl http://localhost:5000/api/rates/USD-RUB?days=30

# Конвертация валют
curl "http://localhost:5000/api/convert?amount=100&from=USD&to=RUB"
```

### Аналитика

```bash
# Анализ валютной пары
curl http://localhost:5000/api/analysis/USD-RUB?days=30

# Поиск арбитража
curl http://localhost:5000/api/arbitrage

# Рейтинг волатильности
curl http://localhost:5000/api/volatility?days=7

# Проверка алертов
curl http://localhost:5000/api/alerts
```

## Python код

### Использование анализатора

```python
from analyzer import CurrencyAnalyzer

analyzer = CurrencyAnalyzer()

# Анализ тренда
trend = analyzer.get_trend_analysis('USD', 'RUB', 7)
print(f"Тренд: {trend}")

# RSI индикатор
rsi = analyzer.get_rsi('USD', 'EUR', 14)
print(f"RSI: {rsi}")

# Прогноз курса
predicted = analyzer.predict_rate('EUR', 'RUB', 7)
print(f"Прогноз: {predicted}")

# Поиск арбитража
opportunities = analyzer.find_arbitrage()
for opp in opportunities:
    print(f"{opp['currency_a']} → {opp['currency_b']} → {opp['currency_c']}: "
          f"+{opp['profit_percent']}%")

# Генерация отчета
report = analyzer.generate_report('USD/RUB', 30)
print(json.dumps(report, indent=2))

analyzer.close()
```

### Визуализация

```python
from visualizer import CurrencyVisualizer

viz = CurrencyVisualizer()

# График истории курса
viz.plot_rate_history('USD', 'RUB', 30, save_path='usd_rub.png')

# Сравнение пар
viz.plot_comparison(['USD/RUB', 'EUR/RUB', 'GBP/RUB'], 30)

# График волатильности
viz.plot_volatility(7, save_path='volatility.png')

viz.close()
```

### Экспорт данных

```python
from exporter import DataExporter

exporter = DataExporter()

# Экспорт в CSV
exporter.export_to_csv('USD', 'RUB', 30, 'usd_rub.csv')

# Экспорт в JSON
exporter.export_to_json('EUR', 'RUB', 30, 'eur_rub.json')

# Экспорт статистики
exporter.export_statistics('stats.json')

exporter.close()
```

## Автоматизация

### Планировщик задач

```python
# Запуск планировщика
python scheduler.py

# Планировщик выполняет:
# - Парсинг: ежедневно в 9:00
# - Проверка алертов: каждый час
# - Расчет статистики: ежедневно в 23:00
```

### Cron (Linux/Mac)

```bash
# Добавьте в crontab
crontab -e

# Парсинг каждый день в 9:00
0 9 * * * cd /path/to/currency-tracker/parser && python main.py

# Проверка алертов каждый час
0 * * * * cd /path/to/currency-tracker/parser && python cli.py alerts

# Расчет статистики в 23:00
0 23 * * * cd /path/to/currency-tracker/parser && python cli.py calculate-stats
```

### Windows Task Scheduler

```powershell
# Создание задачи для парсинга
schtasks /create /tn "Currency Parser" /tr "python C:\path\to\parser\main.py" /sc daily /st 09:00

# Создание задачи для проверки алертов
schtasks /create /tn "Currency Alerts" /tr "python C:\path\to\parser\cli.py alerts" /sc hourly
```

## Интеграция

### Flask приложение

```python
from flask import Flask, jsonify
from analyzer import CurrencyAnalyzer

app = Flask(__name__)

@app.route('/rate/<pair>')
def get_rate(pair):
    base, target = pair.split('-')
    analyzer = CurrencyAnalyzer()
    
    # Получаем последний курс
    db = analyzer.db
    db.cursor.execute("""
        SELECT rate FROM exchange_rates
        WHERE base_currency = %s AND target_currency = %s
        ORDER BY rate_date DESC, created_at DESC
        LIMIT 1
    """, (base, target))
    
    result = db.cursor.fetchone()
    analyzer.close()
    
    return jsonify({
        'pair': pair,
        'rate': float(result[0]) if result else None
    })

if __name__ == '__main__':
    app.run()
```

### Telegram бот

```python
import telebot
from analyzer import CurrencyAnalyzer

bot = telebot.TeleBot('YOUR_TOKEN')

@bot.message_handler(commands=['rate'])
def send_rate(message):
    try:
        pair = message.text.split()[1]  # /rate USD/RUB
        base, target = pair.split('/')
        
        analyzer = CurrencyAnalyzer()
        report = analyzer.generate_report(pair, 7)
        analyzer.close()
        
        response = f"📊 {pair}\n"
        response += f"Тренд: {report['trend']}\n"
        response += f"RSI: {report['rsi']:.2f}\n"
        response += f"Прогноз: {report['predicted_rate']:.4f}"
        
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

bot.polling()
```
