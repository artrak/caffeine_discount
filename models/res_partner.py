from odoo import api, fields, models


class ResPartner(models.Model):

    """
    Extends the ResPartner model to include order information
    and compute total order amounts for each partner.

    This model links partners to their orders and calculates
    the total value of all orders made by the partner.
    """
    _inherit = 'res.partner'

    order_ids = fields.One2many(
        'sale.order',  # Model representing sale orders
        'partner_id',  # Field in the sale order model
        # that refers to the partner
        string='Orders'
    )
    """
    One2many field representing the list of orders linked to this partner.
    Allows tracking of all sale orders associated with the partner.
    """

    total_order_amount = fields.Float(
        string='Total Order Amount',
        compute='_compute_total_order_amount',
        store=True
    )
    """
    Float field representing the total amount of all orders made by the partner
    It is computed automatically by summing up the `amount_total`
    from related orders.
    """

    @api.depends('order_ids.amount_total')
    def _compute_total_order_amount(self):
        """
        Compute the total order amount by summing up the total amounts
        of all related orders for the partner.
        """
        for partner in self:
            partner.total_order_amount \
                = sum(order.amount_total for order in partner.order_ids)
