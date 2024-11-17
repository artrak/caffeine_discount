from datetime import date

from odoo import api, fields, models


class ModelDiscount(models.Model):

    """
       Model representing a Discount in the Caffeine Discount module.

       This model includes various attributes of a discount, such as the
       discount type (percentage or fixed amount), the applicable value,
       the products to which the discount is applicable, and the start
       and end dates that determine if the discount is active.
       """
    _name = 'caffeine_discount.discount'
    _description = 'Discount'

    name = fields.Char(string='Discount Name', required=True)
    """
    Char field representing the name of the discount.
    This field is required to identify the discount uniquely.
    """

    discount_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        string='Type',
        required=True)
    """
    Selection field representing the type of discount.
    It can either be 'percentage' or 'fixed' type, and it is required for
    defining how the discount is applied.
    """

    value = fields.Float(
        string='Value',
        required=True)
    """
    Float field to represent the value of the discount.
    If the discount is a percentage, this value represents
    the percentage discount.
    If it is fixed, this value represents the fixed discount amount.
    """

    product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Applicable Products')
    """
    Many2many field to link the discount to multiple products.
    Defines which products the discount is applicable to.
    """

    start_date = fields.Date()
    """
    Date field to represent the start date of the discount.
    """

    end_date = fields.Date()
    """
    Date field to represent the end date of the discount.
    """

    is_active = fields.Boolean(
        string='Active',
        compute='_compute_is_active',
        default=True,
        store=True)

    @api.depends('start_date', 'end_date')
    def _compute_is_active(self):
        """
        Computes if the discount is currently active based on the start
        and end dates.
        The discount is considered active if today's date is within
        the start and end dates, or if no dates are specified.
        """
        today = date.today()
        for discount in self:
            if not discount.start_date and not discount.end_date:
                discount.is_active = True
            elif discount.start_date and discount.end_date:
                discount.is_active = (
                        discount.start_date <= today <= discount.end_date)
            elif discount.start_date:
                discount.is_active = discount.start_date <= today
            elif discount.end_date:
                discount.is_active = today <= discount.end_date

    @api.model
    def apply_discount(self, product_price):
        """
        Applies the discount to the provided product price based
        on the discount type.
        Returns the discounted price, ensuring that it does not go below zero.

        Args:
            product_price (float): The original price of the product.

        Returns:
            float: The discounted price after applying the discount.
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
