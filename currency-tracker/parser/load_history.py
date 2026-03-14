"""
Загрузка исторических данных с ЦБ РФ и ЕЦБ

Использование:
  python load_history.py          # 6 месяцев (по умолчанию)
  python load_history.py 90       # 90 дней
  python load_history.py 365      # 1 год
  python load_history.py --no-clear  # не очищать БД перед загрузкой
"""
import sys, time, requests
from lxml import etree
from datetime import date, datetime, timedelta
sys.path.insert(0, '.')
from database import Database

CBR_CODES = {
    'USD': 'R01235', 'EUR': 'R01239', 'GBP': 'R01035', 'CNY': 'R01375',
    'JPY': 'R01820', 'CHF': 'R01775', 'CAD': 'R01350', 'AUD': 'R01010',
    'HKD': 'R01200', 'SGD': 'R01740', 'TRY': 'R01700', 'KZT': 'R01335',
    'BYN': 'R01090', 'UAH': 'R01790', 'AMD': 'R01060', 'AZN': 'R01020',
    'KGS': 'R01370', 'UZS': 'R01717', 'GEL': 'R01210', 'MDL': 'R01500',
    'TJS': 'R01760', 'TMT': 'R01670', 'NOK': 'R01535', 'SEK': 'R01770',
    'DKK': 'R01215', 'PLN': 'R01565', 'CZK': 'R01180', 'HUF': 'R01230',
    'RON': 'R01625', 'INR': 'R01270', 'SAR': 'R01750', 'QAR': 'R01580',
}

def fetch_cbr(val_code, date_from, date_to):
    url = (f"https://www.cbr.ru/scripts/XML_dynamic.asp"
           f"?date_req1={date_from.strftime('%d/%m/%Y')}"
           f"&date_req2={date_to.strftime('%d/%m/%Y')}"
           f"&VAL_NM_RQ={val_code}")
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        root = etree.fromstring(resp.content)
        return [(datetime.strptime(r.get('Date'), '%d.%m.%Y').date(),
                 float(r.find('Value').text.replace(',', '.')) / int(r.find('Nominal').text))
                for r in root.findall('Record')]
    except Exception as e:
        print(f"  ERR {val_code}: {e}")
        return []

def load_cbr(db, source_id, date_from, date_to):
    print(f"\n[ЦБ РФ] {date_from} — {date_to}")
    total = 0
    for currency, code in CBR_CODES.items():
        if not db.get_currency_code(currency):
            continue
        records = fetch_cbr(code, date_from, date_to)
        if not records:
            continue
        rows = [(currency, 'RUB', rate, d, source_id) for d, rate in records]
        added = db.insert_rates(rows)
        total += added
        print(f"  {currency}/RUB: {len(records)} дней → +{added}")
        time.sleep(0.1)
    print(f"  Итого ЦБ РФ: {total}")

def load_ecb(db, source_id, days):
    """ЕЦБ: полный архив, фильтруем по периоду"""
    print(f"\n[ЕЦБ] архив (фильтр {days} дней)")
    cutoff = date.today() - timedelta(days=days)
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml"
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        root = etree.fromstring(resp.content)
        ns = {'xmlns': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
        rows = []
        for cube_day in root.findall('.//xmlns:Cube[@time]', ns):
            d = datetime.strptime(cube_day.get('time'), '%Y-%m-%d').date()
            if d < cutoff:
                continue
            for cube_curr in cube_day.findall('xmlns:Cube[@currency]', ns):
                currency = cube_curr.get('currency')
                rate = float(cube_curr.get('rate'))
                if db.get_currency_code(currency):
                    rows.append(('EUR', currency, rate, d, source_id))
        added = db.insert_rates(rows)
        print(f"  Итого ЕЦБ: {added}")
    except Exception as e:
        print(f"  ERR ЕЦБ: {e}")

def main():
    args = sys.argv[1:]
    days = 180
    clear = True

    for arg in args:
        if arg == '--no-clear':
            clear = False
        elif arg.isdigit():
            days = int(arg)

    db = Database()
    db.connect()

    cbr_id = db.get_source_id('Central Bank of Russia')
    ecb_id = db.get_source_id('European Central Bank')

    date_to   = date.today()
    date_from = date_to - timedelta(days=days)

    if clear:
        db.cursor.execute("DELETE FROM exchange_rates")
        db.cursor.execute("DELETE FROM parsing_log")
        db.conn.commit()
        print(f"БД очищена.")

    print(f"Загружаем историю: {date_from} — {date_to} ({days} дней)")

    load_cbr(db, cbr_id, date_from, date_to)
    load_ecb(db, ecb_id, days)

    db.cursor.execute("SELECT COUNT(*), MIN(rate_date), MAX(rate_date) FROM exchange_rates")
    r = db.cursor.fetchone()
    print(f"\n=== Готово: {r[0]} записей, {r[1]} — {r[2]} ===")
    db.disconnect()

if __name__ == '__main__':
    main()
