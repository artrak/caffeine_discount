import logging
from odoo import models, fields, api
from odoo.tools.populate import compute

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order Reference',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        ondelete='cascade',
        string='Product',
        required=True
    )

    discount_id = fields.Many2one(
        comodel_name='caffeine_discount.discount',
        string='Discount'
    )

    discount_value = fields.Float(
        string="Discount Value",
        related='discount_id.value',
        readonly=True
    )

    # named_discount = fields.Float(
    #     string="Named Discount",
    #     compute='_compute_named_discount',
    #     store=True,
    # )

    # @api.depends('order_id.partner_id.total_order_amount')
    # def _compute_named_discount(self):
    #     """
    #     Розрахунок іменної знижки залежно від `Total Order Amount`.
    #     """
    #     for line in self:
    #         total_order_amount = line.order_id.partner_id.total_order_amount
    #         if total_order_amount >= 100:
    #             line.named_discount = 10.0
    #         elif total_order_amount >= 50:
    #             line.named_discount = 7.0
    #         elif total_order_amount >= 20:
    #             line.named_discount = 4.0
    #         elif total_order_amount >= 10:
    #             line.named_discount = 3.0
    #         elif total_order_amount >= 5:
    #             line.named_discount = 2.0
    #         elif total_order_amount >= 1:
    #             line.named_discount = 1.0
    #         else:
    #             line.named_discount = 0.0

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id(self):
        self._compute_best_discount()

    @api.depends('product_id', 'product_uom_qty', 'price_unit')
    def _compute_best_discount(self):
        """
        Автоматично вибирає найвигідніший дисконт для продукту та логує вибір.
        """
        for line in self:
            best_discount = None
            max_discount_amount = 0
            discount_amount = 0

            _logger.info(
                "-----------------------------------------------------------------------------"
            )
            for discount in line.product_id.discount_ids:
                # Перевіряємо, чи дисконт активний
                if discount.is_active:
                    _logger.info(
                        "Found active discount: %s, Type: %s, Value: %s",
                        discount.name, discount.discount_type, discount.value
                    )

                    # Розрахунок суми знижки для кожного дисконту
                    if discount.discount_type == 'percentage':
                        discount_amount = line.price_unit * (
                                    discount.value / 100)
                    elif discount.discount_type == 'fixed':
                        discount_amount = discount.value
                    else:
                        # Якщо тип не відомий, логувати попередження
                        _logger.warning(
                            "Unknown discount type for discount: %s",
                            discount.name)

                    _logger.info(
                        "Discount amount for>>>>>>>>>>>>>>>>>>>> %s: %s, Value: %s",
                        discount.name,
                        discount_amount,
                        discount.value
                    )

                    # Вибір дисконту з найбільшою знижкою
                    if discount_amount > max_discount_amount:
                        max_discount_amount = discount_amount
                        best_discount = discount

            # line.amount_tax = 0

            if best_discount:
                line.discount_id = best_discount
            else:
                line.discount_id = False



    # @api.depends('product_uom_qty', 'price_unit', 'discount_id', 'named_discount')
    # def _compute_amount(self):
    #     super(SaleOrderLine, self)._compute_amount()
    #     for line in self:
    #         discount_amount = 0
    #         if line.discount_id:
    #             if line.discount_id.discount_type == 'percentage':
    #                 discount_amount = line.price_unit * (line.discount_id.value / 100)
    #             elif line.discount_id.discount_type == 'fixed':
    #                 discount_amount = line.discount_id.value
    #         else:
    #             discount_amount = line.price_unit * (line.named_discount / 100)
    #
    #         line.price_subtotal = line.product_uom_qty * (line.price_unit - discount_amount)



    @api.depends('product_uom_qty', 'discounted_price_unit')
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.discounted_price_unit

    @api.depends('product_uom_qty', 'price_unit', 'discount_id')
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()  # Правильне використання методу super
        for line in self:
            discount_amount = 0
            if line.discount_id:
                if line.discount_id.discount_type == 'percentage':
                    discount_amount = line.price_unit * (line.discount_id.value / 100)
                elif line.discount_id.discount_type == 'fixed':
                    discount_amount = line.discount_id.value

            line.price_subtotal = line.product_uom_qty * (line.price_unit - discount_amount)

    @api.model
    def create(self, vals):
        """
        Викликається при створенні рядка замовлення і застосовує найвигідніший дисконт.
        """
        line = super(SaleOrderLine, self).create(vals)
        line._compute_best_discount()
        return line
