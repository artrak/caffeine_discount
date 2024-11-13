from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    client_id = fields.Many2one(
        comodel_name='caffeine_discount.client',
        string='Client',
        required=True
    )

    barista_id = fields.Many2one(
        comodel_name='caffeine_discount.barista',
        string='Barista'
    )

    order_date = fields.Datetime(
        string='Order Date (Custom)',
        default=fields.Datetime.now,
        required=True
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        default=lambda self: self.env.user.partner_id
    )

    # amount_total = fields.Monetary(
    #     string='Total Amount',
    #     compute='_compute_amount_total',
    #     store=True,
    #     readonly=True,
    #     currency_field='currency_id'
    # )

    @api.depends('order_line.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(line.price_subtotal for line in order.order_line)


    @api.model
    def default_get(self, fields_list):
        # Отримуємо стандартні значення
        res = super(SaleOrder, self).default_get(fields_list)
        # Якщо partner_id ще не встановлено, присвоюємо його як поточного користувача
        if 'partner_id' in fields_list and not res.get('partner_id'):
            res['partner_id'] = self.env.user.partner_id.id
        return res

    @api.model
    def create(self, vals):
        # Якщо partner_id не встановлено у значеннях, присвоюємо поточного користувача
        if 'partner_id' not in vals or not vals['partner_id']:
            vals['partner_id'] = self.env.user.partner_id.id
        # Перевірка наявності обов'язкових полів client_id та barista_id
        if 'client_id' not in vals or not vals['client_id']:
            raise ValueError("The field 'Client' is mandatory.")
        if 'barista_id' not in vals or not vals['barista_id']:
            raise ValueError("The field 'Barista' is mandatory.")
        return super(SaleOrder, self).create(vals)

    @api.depends('order_line.price_total')
    def _compute_amount_total(self):
        super(SaleOrder, self)._compute_amount_total()
        for order in self:
            discount_amount = 0
            if order.discount_id:
                if order.discount_id.discount_type == 'percentage':
                    discount_amount = order.amount_untaxed * (order.discount_id.value / 100)
                elif order.discount_id.discount_type == 'fixed':
                    discount_amount = order.discount_id.value
            order.amount_untaxed -= discount_amount

    def print_receipt(self):
        return self.env.ref('caffeine_discount.report_sale_order_receipt').report_action(self)
