from odoo import fields, models


class ModelProduct(models.Model):

    """
    Extends the Product model to include additional fields
    and functionality for the Caffeine Discount module.

    This model adds support for product categories, discounts,
    and stock management.
    """
    _inherit = 'product.product'

    category = fields.Selection([
        ('drink', 'Drink'),
        ('food', 'Food'),
        ('coffee', 'Coffee')
    ], string='Category', required=False)
    """
    Selection field to represent the category of the product.
    Categories include 'Drink', 'Food', and 'Coffee'.
    This field is not mandatory.
    """

    category_id = fields.Many2one(
        comodel_name='product.template',
        required=False)
    """
    Many2one field to represent the category template associated
    with the product.
    This field is optional.
    """


    discount_ids = fields.Many2many(
        'caffeine_discount.discount',
        string='Discounts'
    )
    """
    Many2many field linking the product to multiple discounts.
    Allows multiple discounts to be applicable to this product.
    """


    stock = fields.Integer(string='Stock Quantity', default=0)
    """
    Integer field to store the current stock quantity of the product.
    Defaults to zero.
    """
