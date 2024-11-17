from odoo import fields, models


class ModelBarista(models.Model):

    """
    Model representing a Barista in the Caffeine Discount module.

    This model extends the person mixin to include additional information
    specific to baristas, such as shifts, orders managed by the barista,
    and discount types applied by them.
    """
    _inherit = 'caffeine_discount.person.mixin'
    _name = 'caffeine_discount.barista'
    _description = 'Barista'

    shift = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening')
    ], string='Shift')
    """
    Selection field to indicate the work shift of the barista.
    Values can be 'morning', 'afternoon', or 'evening'.
    """

    order_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='barista_id',
        string='Orders'
    )
    """
    One2many field representing the list of orders handled by the barista.
    Links to the 'sale.order' model with the 'barista_id' field.
    """

    discount_type = fields.Char()
    """
    Field to indicate the type of discount the barista might be authorized
    to apply.
    """
