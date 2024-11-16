from odoo import fields, models, api


class ModelProduct(models.Model):
    _inherit = 'product.product'

    category = fields.Selection([
        ('drink', 'Drink'),
        ('food', 'Food'),
        ('coffee', 'Coffee')
    ], string='Category', required=False)

    category_id = fields.Many2one(
        comodel_name='product.template',
        required=False)


    discount_ids = fields.Many2many(
        'caffeine_discount.discount',
        string='Discounts'
    )

    stock = fields.Integer(string='Stock Quantity', default=0)

    # photo = fields.Image("Photo", max_width=1024, max_height=1024)
