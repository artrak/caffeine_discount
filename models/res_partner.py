from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_order_amount = fields.Float(
        string='Total Order Amount',
        compute='_compute_total_order_amount',
        store=True,
    )

    @api.depends('sale_order_ids.amount_total')
    def _compute_total_order_amount(self):
        """
        Обчислює загальну суму замовлень клієнта.
        """
        for partner in self:
            partner.total_order_amount = sum(order.amount_total for order in partner.sale_order_ids)
