from odoo.tests.common import TransactionCase
from datetime import datetime


class CaffeineDiscountCommon(TransactionCase):

    def setUp(self):
        super(CaffeineDiscountCommon, self).setUp()
        self.client = self.env['caffeine_discount.client'].create({
            'name': 'Artem Rudko',
            'gender': 'male',
            'birth_date': '1990-01-01',
            'loyalty_points': 10,
            'phone': '+380671234567',
            'email': 'artem@example.com',
        })

        self.barista = self.env['caffeine_discount.barista'].create({
            'name': 'Ivan Karpenko',
            'gender': 'male',
            'shift': 'morning',
            'phone': '+380672345678',
            'email': 'ivan@example.com',
        })

        self.product = self.env['product.product'].create({
            'name': 'Cappuccino',
            'list_price': 50.0,
            'category': 'coffee',
        })

        self.discount = self.env['caffeine_discount.discount'].create({
            'name': '10% на каву',
            'discount_type': 'percentage',
            'value': 10,
        })

        self.order = self.env['sale.order'].create({
            'client_id': self.client.id,
            'barista_id': self.barista.id,
            'order_date': datetime.now(),
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 2,
                    'price_unit': self.product.list_price,
                })
            ]
        })
