import requests
from lxml import etree
from datetime import datetime

class ECBParser:
    """Парсер данных Европейского Центрального Банка"""
    
    def __init__(self, url):
        self.url = url
        self.base_currency = 'EUR'
    
    def fetch(self):
        """Получение данных с сайта ЕЦБ"""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise Exception(f"Ошибка загрузки данных ЕЦБ: {e}")
    
    def parse(self, xml_data):
        """Парсинг XML данных ЕЦБ"""
        rates = []
        
        try:
            root = etree.fromstring(xml_data)
            
            # Namespace для ECB XML
            ns = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
                  'xmlns': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
            
            cube = root.find('.//xmlns:Cube[@time]', ns)
            if cube is None:
                raise Exception("Не найдены данные о курсах")
            
            rate_date_str = cube.get('time')
            rate_date = datetime.strptime(rate_date_str, '%Y-%m-%d').date()
            
            for currency_cube in cube.findall('xmlns:Cube[@currency]', ns):
                currency = currency_cube.get('currency')
                rate = float(currency_cube.get('rate'))
                
                rates.append({
                    'base_currency': self.base_currency,
                    'target_currency': currency,
                    'rate': rate,
                    'rate_date': rate_date
                })
            
            return rates
        except Exception as e:
            raise Exception(f"Ошибка парсинга данных ЕЦБ: {e}")
