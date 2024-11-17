from odoo import api, fields, models


class SaleOrder(models.Model):

    """
    Extends the Sale Order model to include custom fields specific
    to the Caffeine Discount module.

    This model includes information about the client, barista,
    custom order date, and modifications to partner interactions
    and calculations related to discounts.
    """
    _inherit = 'sale.order'

    client_id = fields.Many2one(
        comodel_name='caffeine_discount.client',
        string='Client',
        required=True
    )
    """
    Many2one field representing the client associated with this sale order.
    Links to the 'caffeine_discount.client' model.
    This field is required to properly associate an order with a client.
    """

    barista_id = fields.Many2one(
        comodel_name='caffeine_discount.barista',
        string='Barista'
    )
    """
    Many2one field representing the barista handling the sale order.
    Links to the 'caffeine_discount.barista' model.
    """

    order_date = fields.Datetime(
        string='Order Date (Custom)',
        default=fields.Datetime.now,
        required=True
    )
    """
    Datetime field for the date of the order.
    Defaults to the current datetime and is required.
    """

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        ondelete='cascade',
        required=True,
        default=lambda self: self.env.user.partner_id
    )
    """
    Many2one field representing the customer associated with the sale order.
    Defaults to the current user's partner.
    """

    def print_receipt(self):
        return self.env.ref(
            'caffeine_discount.report_sale_order_receipt').report_action(self)

    @api.model
    def default_get(self, fields_list):
        """
        Provides default values for fields when creating a new record.
        Specifically, it ensures that the 'partner_id' field defaults
        to the current user's partner.

        Args:
            fields_list (list): List of fields to get defaults for.

        Returns:
            dict: Default values for the given fields.
        """
        # Отримуємо стандартні значення
        res = super(SaleOrder, self).default_get(fields_list)
        # Якщо partner_id ще не встановлено, присвоюємо його як поточного користувача
        if 'partner_id' in fields_list and not res.get('partner_id'):
            res['partner_id'] = self.env.user.partner_id.id
        return res

    @api.model
    def create(self, vals):
        """
        Creates a new Sale Order record, ensuring required fields
        are properly set.
        If 'partner_id', 'client_id', or 'barista_id' are missing,
        defaults or raises errors accordingly.

        Args:
            vals (dict): Values for the new record.

        Returns:
            recordset: Newly created Sale Order record.
        """
        # Set partner_id to the current user's partner if not provided
        if 'partner_id' not in vals or not vals['partner_id']:
            vals['partner_id'] = self.env.user.partner_id.id
        # Ensure client_id and barista_id are provided
        if 'client_id' not in vals or not vals['client_id']:
            raise ValueError("The field 'Client' is mandatory.")
        if 'barista_id' not in vals or not vals['barista_id']:
            raise ValueError("The field 'Barista' is mandatory.")
        return super(SaleOrder, self).create(vals)

    @api.onchange('barista_id')
    def _onchange_barista_id(self):
        """
        Triggered when the 'barista_id' field is changed.
        Updates the 'partner_id' with the selected barista's partner.
        """
        if self.barista_id and self.barista_id.partner_id:
            self.partner_id = self.barista_id.partner_id

    def print_receipt(self):
        """
        Prints a receipt for the current sale order.

        Returns:
            Action to generate the receipt report.
        """
        return (self.env.ref('caffeine_discount.report_sale_order_receipt')
                .report_action(self))

    @api.depends('order_line.price_subtotal', 'order_line.price_total',
                 'discount_id')
    def _compute_amount_total(self):
        """
        Computes the total amounts for the sale order, considering discounts
        and taxes.
        Updates the 'amount_untaxed', 'amount_tax', and 'amount_total' fields.
        """
        for order in self:
            # Calculate the untaxed amount by summing up the price_subtotal
            # for each order line
            amount_untaxed = sum(
                line.price_subtotal for line in order.order_line)
            # Calculate the total tax amount by summing up the price_tax
            # for each order line
            amount_tax = sum(line.price_tax for line in order.order_line)

            # Calculate discount amount based on discount type (if any)
            discount_amount = 0
            if order.discount_id:
                if order.discount_id.discount_type == 'percentage':
                    discount_amount = amount_untaxed * (
                                order.discount_id.value / 100)
                elif order.discount_id.discount_type == 'fixed':
                    discount_amount = order.discount_id.value

            # Apply the discount to the untaxed amount
            amount_untaxed -= discount_amount

            # Update the computed fields
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })
