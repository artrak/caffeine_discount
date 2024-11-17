import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):

    """
    Extends the Sale Order Line model to include additional fields
    and functionality for the Caffeine Discount module.

    This model allows the application of different discounts and computes
    the best possible discount for each order line.
    """
    _inherit = 'sale.order.line'

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order Reference',
        required=True,
        ondelete='cascade'
    )
    """
    Many2one field representing the reference to the sale order.
    It is a required field and will be deleted if the associated
    sale order is deleted.
    """
    product_id = fields.Many2one(
        comodel_name='product.product',
        ondelete='cascade',
        string='Product',
        required=True
    )
    """
    Many2one field representing the product associated with this
    sale order line.
    It is required and will be deleted if the product is deleted.
    """

    discount_id = fields.Many2one(
        comodel_name='caffeine_discount.discount',
        string='Discount'
    )
    """
    Many2one field representing the discount applied to the sale order line.
    Links to the 'caffeine_discount.discount' model.
    """

    discount_value = fields.Float(
        string="Discount Value",
        related='discount_id.value',
        readonly=True
    )
    """
    Related field that shows the value of the discount applied to this line.
    This value is read-only and is pulled from the linked discount record.
    """

    named_discount = fields.Float(
        string="Named Discount",
        compute='_compute_named_discount',
        store=True
    )
    """
    Float field representing a named discount computed based
    on the client's total order amount.
    It is stored in the database and recalculated when needed.
    """

    @api.depends('order_id.partner_id.total_order_amount')
    def _compute_named_discount(self):
        """
        Compute the named discount based on the total order amount
        of the client.
        Discounts are tiered based on predefined thresholds
        for the client's total order amount.
        """
        for line in self:
            if line.order_id.partner_id and hasattr(line.order_id.partner_id,
                                                    'total_order_amount'):
                total_order_amount = line.order_id.partner_id.total_order_amount
                if total_order_amount >= 100:
                    line.named_discount = 10.0
                elif total_order_amount >= 50:
                    line.named_discount = 7.0
                elif total_order_amount >= 20:
                    line.named_discount = 4.0
                elif total_order_amount >= 10:
                    line.named_discount = 3.0
                elif total_order_amount >= 5:
                    line.named_discount = 2.0
                elif total_order_amount >= 1:
                    line.named_discount = 1.0
                else:
                    line.named_discount = 0.0
            else:
                line.named_discount = 0.0

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id(self):
        """
        Triggered when the product or quantity changes
        for the sale order line.
        This method recomputes the best possible discount
        available for the product.
        """
        self._compute_best_discount()

    @api.depends('product_uom_qty', 'price_unit', 'discount_id',
                 'named_discount')
    def _compute_amount(self):
        """
        Compute the amount for the sale order line,
        taking into account discounts.
        Uses both named and specific discounts to calculate
        the final subtotal for the line.
        """
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            discount_amount = 0
            # Check if the product has active discount
            if line.discount_id and line.discount_id.is_active:
                if line.discount_id.discount_type == 'percentage':
                    discount_amount = line.price_unit * (
                                line.discount_id.value / 100)
                elif line.discount_id.discount_type == 'fixed':
                    discount_amount = line.discount_id.value

            # Compare with named discount
            named_discount_amount = line.price_unit * (
                        line.named_discount / 100)
            if named_discount_amount > discount_amount:
                discount_amount = named_discount_amount

            line.price_subtotal = line.product_uom_qty * (
                        line.price_unit - discount_amount)

    @api.depends('product_id', 'product_uom_qty', 'price_unit')
    def _compute_best_discount(self):
        """
        Automatically selects the best possible discount
        for the product and logs the selection.
        Logs details about each discount and selects
        the one offering the highest discount.
        """
        for line in self:
            best_discount = None
            max_discount_amount = 0
            discount_amount = 0

            for discount in line.product_id.discount_ids:
                # Check if the discount is active
                if discount.is_active:
                    _logger.info(
                        "Found active discount: %s, Type: %s, Value: %s",
                        discount.name, discount.discount_type, discount.value
                    )

                    # Calculate discount amount for each discount
                    if discount.discount_type == 'percentage':
                        discount_amount = line.price_unit * (
                                    discount.value / 100)
                    elif discount.discount_type == 'fixed':
                        discount_amount = discount.value
                    else:
                        _logger.warning(
                            "Unknown discount type for discount: %s",
                            discount.name)

                    # Log and select the discount with the highest value
                    if discount_amount > max_discount_amount:
                        max_discount_amount = discount_amount
                        best_discount = discount

            # Assign the best discount found or clear the discount if none
            if best_discount:
                line.discount_id = best_discount
            else:
                line.discount_id = False

    @api.depends('product_uom_qty', 'discounted_price_unit')
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.discounted_price_unit

    @api.depends('product_uom_qty', 'price_unit', 'discount_id')
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()
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
        Called when creating a sale order line.
        Applies the best possible discount to the line upon creation.

        Args:
            vals (dict): Values for the new sale order line.

        Returns:
            recordset: Newly created Sale Order Line record with
            the best discount applied.
        """
        line = super(SaleOrderLine, self).create(vals)
        line._compute_best_discount()
        return line
