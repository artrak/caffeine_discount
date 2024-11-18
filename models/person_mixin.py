import logging

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonMixin(models.AbstractModel):

    """
    Abstract model representing a person in the Caffeine Discount module.
    This mixin includes common attributes such as name, gender,
    birth date, age, contact details, and partner linkage.
    """
    _name = 'caffeine_discount.person.mixin'
    _description = 'Abstract Model for Person'

    name = fields.Char(
        required=True,
        store=True,
    )
    """
    Char field to store the name of the person.
    This is a required field.
    """

    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        required=True,
    )
    """
    Selection field to indicate the gender of the person.
    The available options are 'male' and 'female'.
    This is a required field.
    """

    birth_date = fields.Date(string="Date of Birth")
    """
    Date field to store the date of birth of the person.
    """

    age = fields.Integer(
        compute='_compute_age',
        store=True,
    )
    """
    Integer field to store the computed age of the person.
    It is computed automatically based on the birth date.
    """

    photo = fields.Binary("Photo", attachment=True)
    """
    Binary field to store a photo of the person.
    This field allows uploading and storing an image as an attachment.
    """

    phone = fields.Char()
    """
    Char field to store the phone number of the person.
    """

    email = fields.Char()
    """
    Char field to store the email address of the person.
    """

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Related Partner'
    )
    """
    Many2one field to link the person to a partner record in Odoo.
    It represents the relationship between this person
    and the `res.partner` model.
    """

    total_order_amount = fields.Float(
        string='Total Order Amount',
        compute='_compute_total_order_amount',
        store=True
    )
    """
    Float field representing the total amount of all orders made by the person.
    It is computed automatically by summing up the `amount_total` 
    of related orders.
    """

    @api.depends('order_ids.amount_total')
    def _compute_total_order_amount(self):
        """
        Compute the total order amount for the person by summing up
        the total amounts of all related orders.
        """
        for client in self:
            client.total_order_amount \
                = sum(order.amount_total for order in client.order_ids)

    @api.model
    def create(self, vals):
        """
        Create a new person record, ensuring that a corresponding
        partner record is also created.
        If no `partner_id` is provided, a new partner is created
        using the person's details.

        Args:
            vals (dict): Values for the new person record.

        Returns:
            recordset: The newly created person record.
        """
        if 'partner_id' not in vals:
            partner_vals = {
                'name': vals.get('name'),
                'phone': vals.get('phone'),
                'mobile': vals.get('phone'),
                'email': vals.get('email'),
                'loyalty_points': vals.get('loyalty_points', 0),
            }
            partner = self.env['res.partner'].create(partner_vals)
            vals['partner_id'] = partner.id
        return super(PersonMixin, self).create(vals)

    @api.depends('birth_date')
    def _compute_age(self):
        """
        Compute the age of the person based on their birth date.
        If the birth date is not set, the age defaults to zero.
        """
        for record in self:
            if record.birth_date:
                record.age = relativedelta(fields.Date.today(),
                                           record.birth_date).years
            else:
                record.age = 0
