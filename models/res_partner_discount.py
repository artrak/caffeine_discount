from odoo import models, fields, api


class ResPartnerDiscount(models.Model):
    _inherit = 'res.partner'

    discount_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage')
    ], string="Discount Type", default='percent')

    discount_value = fields.Float(string="Discount Value")
    loyalty_points = fields.Integer(string="Loyalty Points", default=0)

    def calculate_discount(self, amount):
        self.ensure_one()
        if self.discount_type == 'percent':
            return amount * (self.discount_value / 100)
        elif self.discount_type == 'fixed':
            return min(amount, self.discount_value)
        return 0.0

    def update_loyalty_points(self, amount):
        points_earned = amount // 10
        self.loyalty_points += points_earned
