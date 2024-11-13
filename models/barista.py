from odoo import fields, models, api


class ModelBarista(models.Model):
    _inherit = 'caffeine_discount.person.mixin'
    _name = 'caffeine_discount.barista'
    _description = 'Barista'

    shift = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening')
    ], string='Shift')

    order_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='barista_id',
        string='Orders'
    )

    discount_type = fields.Char()
