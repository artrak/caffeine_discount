from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    order_ids = fields.One2many(
        'sale.order',  # або ваша модель замовлень
        'partner_id',  # поле в моделі замовлень, що посилається на партнера
        string='Orders'
    )

    total_order_amount = fields.Float(
        string='Total Order Amount',
        compute='_compute_total_order_amount',
        store=True
    )

    @api.depends('order_ids.amount_total')
    def _compute_total_order_amount(self):
        for partner in self:
            partner.total_order_amount = sum(order.amount_total for order in partner.order_ids)
