from odoo import fields, models, api
from datetime import date


class ModelDiscount(models.Model):
    _name = 'caffeine_discount.discount'
    _description = 'Discount'

    name = fields.Char(string='Discount Name', required=True)

    discount_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        string='Type',
        required=True)

    value = fields.Float(
        string='Value',
        required=True)

    product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Applicable Products')

    start_date = fields.Date()

    end_date = fields.Date()

    is_active = fields.Boolean(
        string='Active',
        compute='_compute_is_active',
        default=True,
        store=True)

    @api.depends('start_date', 'end_date')
    def _compute_is_active(self):
        """
        Computes if the discount is currently active based on the start and end dates.
        """
        today = date.today()
        for discount in self:
            # Вважається активним, якщо немає дат, або сьогоднішня дата в межах періоду.
            if not discount.start_date and not discount.end_date:
                discount.is_active = True
            elif discount.start_date and discount.end_date:
                discount.is_active = discount.start_date <= today <= discount.end_date
            elif discount.start_date:
                discount.is_active = discount.start_date <= today
            elif discount.end_date:
                discount.is_active = today <= discount.end_date

    @api.model
    def apply_discount(self, product_price):
        """
        Applies the discount to the provided product price based on the discount type.
        Returns the discounted price.
        """
        discounted_price = product_price
        if self.is_active:
            if self.discount_type == 'percentage':
                discount_amount = product_price * (self.value / 100)
            elif self.discount_type == 'fixed':
                discount_amount = self.value
            discounted_price = max(product_price - discount_amount,
                                   0)  # Ensure price is not negative
        return discounted_price