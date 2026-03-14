#!/usr/bin/env python3
"""
REST API сервер для Currency Tracker
"""

from flask import Flask, jsonify, request
from analyzer import CurrencyAnalyzer
from database import Database
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/rates/latest', methods=['GET'])
def get_latest_rates():
    """Получить последние курсы"""
    db = Database()
    db.connect()
    
    query = "SELECT * FROM v_latest_rates"
    db.cursor.execute(query)
    results = db.cursor.fetchall()
    
    rates = []
    for row in results:
        rates.append({
            'base_currency': row[0],
            'target_currency': row[1],
            'currency_pair': row[2],
            'rate': float(row[3]),
            'rate_date': row[4].isoformat(),
            'source_name': row[5]
        })
    
    db.disconnect()
    return jsonify(rates)

@app.route('/api/rates/<pair>', methods=['GET'])
def get_rate_history(pair):
    """История курса валютной пары"""
    days = request.args.get('days', 30, type=int)
    base, target = pair.split('-')
    
    db = Database()
    db.connect()
    
    query = """
        SELECT rate_date, rate
        FROM exchange_rates
        WHERE base_currency = %s 
          AND target_currency = %s
          AND rate_date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY rate_date
    """
    db.cursor.execute(query, (base, target, days))
    results = db.cursor.fetchall()
    
    history = []
    for row in results:
        history.append({
            'date': row[0].isoformat(),
            'rate': float(row[1])
        })
    
    db.disconnect()
    return jsonify(history)

@app.route('/api/convert', methods=['GET'])
def convert_currency():
    """Конвертация валют"""
    amount = request.args.get('amount', type=float)
    from_curr = request.args.get('from')
    to_curr = request.args.get('to')
    
    if not all([amount, from_curr, to_curr]):
        return jsonify({'error': 'Missing parameters'}), 400
    
    db = Database()
    db.connect()
    
    query = "SELECT convert_currency(%s, %s, %s)"
    db.cursor.execute(query, (amount, from_curr, to_curr))
    result = db.cursor.fetchone()
    
    db.disconnect()
    
    return jsonify({
        'amount': amount,
        'from': from_curr,
        'to': to_curr,
        'result': float(result[0]) if result else None
    })

@app.route('/api/analysis/<pair>', methods=['GET'])
def analyze_pair(pair):
    """Анализ валютной пары"""
    days = request.args.get('days', 30, type=int)
    
    analyzer = CurrencyAnalyzer()
    report = analyzer.generate_report(pair.replace('-', '/'), days)
    analyzer.close()
    
    return jsonify(report)

@app.route('/api/arbitrage', methods=['GET'])
def find_arbitrage():
    """Поиск арбитража"""
    analyzer = CurrencyAnalyzer()
    opportunities = analyzer.find_arbitrage()
    analyzer.close()
    
    return jsonify(opportunities)

@app.route('/api/volatility', methods=['GET'])
def get_volatility():
    """Рейтинг волатильности"""
    days = request.args.get('days', 7, type=int)
    
    analyzer = CurrencyAnalyzer()
    ranking = analyzer.get_volatility_ranking(days)
    analyzer.close()
    
    return jsonify(ranking)

@app.route('/api/alerts', methods=['GET'])
def check_alerts():
    """Проверка алертов"""
    analyzer = CurrencyAnalyzer()
    alerts = analyzer.check_alerts()
    analyzer.close()
    
    return jsonify(alerts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
