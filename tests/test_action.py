from datetime import datetime
from odoo.addons.caffeine_discount.tests.common import CaffeineDiscountCommon
from odoo.exceptions import UserError

class TestCaffeineDiscount(CaffeineDiscountCommon):

    def test_01_apply_discount(self):
        """Test that discount is applied correctly to the product price"""
        expected_discount_price = self.product.list_price * (1 - self.discount.value / 100)
        discounted_price = self.discount.apply_discount(self.product.list_price)
        self.assertEqual(discounted_price, expected_discount_price,
                         "Discount application is incorrect")

    def test_02_loyalty_points_calculation(self):
        """Test that loyalty points are calculated correctly for an order"""
        self.order._compute_loyalty_points()
        expected_points = self.order.amount_total // 10
        self.assertEqual(self.client.loyalty_points, expected_points + 10,
                         "Loyalty points calculation is incorrect")

    def test_03_cannot_delete_approved_order(self):
        """Test that an approved order cannot be deleted"""
        self.order.write({'state': 'approved'})
        with self.assertRaises(UserError):
            self.order.unlink()

    def test_04_shift_validation(self):
        """Test that the barista's shift is validated correctly"""
        with self.assertRaises(UserError):
            self.barista.shift = 'night'  # Invalid value

    def test_05_client_order_restriction(self):
        """Test that a client can only place one order at a time"""
        with self.assertRaises(UserError):
            self.env['sale.order'].create({
                'client_id': self.client.id,
                'barista_id': self.barista.id,
                'order_date': datetime.now(),
                'order_line': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'product_uom_qty': 1,
                        'price_unit': self.product.list_price,
                    })
                ]
            })
