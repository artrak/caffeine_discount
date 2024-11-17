from odoo import fields, models


class ModelClient(models.Model):

    """
    Model representing a Client in the Caffeine Discount module.

    This model extends the person mixin to include additional
    information specific to clients, such as loyalty points,
    orders placed by the client, and their address.
    """
    _inherit = 'caffeine_discount.person.mixin'
    _name = 'caffeine_discount.client'
    _description = 'Client'

    loyalty_points = fields.Integer(string='Loyalty Points', default=0)
    """
    Integer field to store the number of loyalty points accumulated
    by the client.
    Default value is set to 0.
    """
    order_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='client_id',
        string='Orders'
    )
    """
    One2many field representing the list of orders placed by the client.
    Links to the 'sale.order' model with the 'client_id' field.
    """
    address = fields.Char(string='Address')
    """
    Char field to store the address of the client.
    """
