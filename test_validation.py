import unittest
from validation import verify_price, cheapest_available_cement

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = dict(requested_city='Valdivia', selected_store='Local Valdivia',
                         confirmed_store_city='Valdivia', displayed_price=5090,
                         currency='CLP', product_sku='110324015',
                         confirmed_sku='110324015', stock_status='available',
                         source_url='https://example.com/item')

    def test_verified(self):
        self.assertEqual(verify_price(**self.data)['status'], 'VERIFIED')

    def test_wrong_city(self):
        self.assertEqual(verify_price(**(self.data | {'confirmed_store_city':'Osorno'}))['reason'], 'STORE_NOT_CONFIRMED')

    def test_missing_store(self):
        self.assertEqual(verify_price(**(self.data | {'selected_store':None}))['reason'], 'STORE_NOT_CONFIRMED')

    def test_wrong_product(self):
        self.assertEqual(verify_price(**(self.data | {'confirmed_sku':'other'}))['reason'], 'PRODUCT_NOT_CONFIRMED')

    def test_bad_price(self):
        self.assertEqual(verify_price(**(self.data | {'displayed_price':'$5.090'}))['reason'], 'PRICE_NOT_CONFIRMED')

    def test_missing_stock(self):
        self.assertEqual(verify_price(**(self.data | {'stock_status':None}))['reason'], 'STOCK_NOT_CONFIRMED')

    def test_cheapest_available(self):
        rows = [dict(category='cement_25kg', brand='Melón', status='VERIFIED', stock='available', price_clp=5200),
                dict(category='cement_25kg', brand='Polpaico', status='VERIFIED', stock='available', price_clp=4990),
                dict(category='cement_25kg', brand='Melón', status='UNVERIFIED', stock='available', price_clp=1)]
        self.assertEqual(cheapest_available_cement(rows)['brand'], 'Polpaico')

if __name__ == '__main__':
    unittest.main()
