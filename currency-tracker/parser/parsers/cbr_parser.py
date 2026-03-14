import requests
from lxml import etree
from datetime import datetime

class CBRParser:
    """Парсер данных Центрального Банка России"""
    
    def __init__(self, url):
        self.url = url
        self.base_currency = 'RUB'
    
    def fetch(self):
        """Получение данных с сайта ЦБ РФ"""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise Exception(f"Ошибка загрузки данных ЦБ РФ: {e}")
    
    def parse(self, xml_data):
        """Парсинг XML данных ЦБ РФ"""
        rates = []
        
        try:
            root = etree.fromstring(xml_data)
            rate_date_str = root.get('Date')
            rate_date = datetime.strptime(rate_date_str, '%d.%m.%Y').date()
            
            for valute in root.findall('Valute'):
                char_code = valute.find('CharCode').text
                nominal = int(valute.find('Nominal').text)
                value = float(valute.find('Value').text.replace(',', '.'))
                
                # Курс за единицу валюты
                rate = value / nominal
                
                rates.append({
                    'base_currency': char_code,
                    'target_currency': self.base_currency,
                    'rate': rate,
                    'rate_date': rate_date
                })
            
            return rates
        except Exception as e:
            raise Exception(f"Ошибка парсинга данных ЦБ РФ: {e}")
