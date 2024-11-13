from odoo import fields, models, api


class ModelClient(models.Model):
    _inherit = 'caffeine_discount.person.mixin'
    _name = 'caffeine_discount.client'
    _description = 'Client'

    loyalty_points = fields.Integer(string='Loyalty Points', default=0)
    order_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='partner_id',
        string='Orders'
    )
    address = fields.Char(string='Address')
