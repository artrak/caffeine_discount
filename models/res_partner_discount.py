from odoo import fields, models


class ResPartnerDiscount(models.Model):

    """
    Extends the ResPartner model to add discount
    and loyalty management for the Caffeine Discount module.

    This model includes fields and methods
    for managing partner-specific discounts and loyalty points.
    """
    _inherit = 'res.partner'

    discount_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage')
    ], string="Discount Type", default='percent')
    """
    Selection field representing the type of discount applicable to the partner
    It can either be a fixed amount or a percentage. Defaults to 'percent'.
    """

    discount_value = fields.Float(string="Discount Value")
    """
    Float field representing the value of the discount.
    If the discount type is 'fixed', it represents a fixed discount amount.
    If the discount type is 'percent', it represents a percentage discount.
    """

    loyalty_points = fields.Integer(string="Loyalty Points", default=0)
    """
    Integer field representing the number of loyalty points accumulated
    by the partner.
    Defaults to zero.
    """

    def calculate_discount(self, amount):
        """
        Calculate the discount for a given amount based on the partner's
        discount type and value.

        Args:
            amount (float): The original amount before discount.

        Returns:
            float: The calculated discount value.
        """
        self.ensure_one()
        if self.discount_type == 'percent':
            # Calculate discount as a percentage of the amount
            return amount * (self.discount_value / 100)
        elif self.discount_type == 'fixed':
            # Ensure the fixed discount does not exceed the original amount
            return min(amount, self.discount_value)
        return 0.0

    def update_loyalty_points(self, amount):
        """
        Update the loyalty points of the partner based on the provided amount.
        Points are earned at a rate of 1 point for every 10 currency
        units spent.

        Args:
            amount (float): The amount spent by the partner.
        """
        points_earned = amount // 10  # Calc points earned based
        # on amount spent
        self.loyalty_points += points_earned
