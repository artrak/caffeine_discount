import logging
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
_logger = logging.getLogger(__name__)


class PersonMixin(models.AbstractModel):
    _name = 'caffeine_discount.person.mixin'
    _description = 'Abstract Model for Person'

    name = fields.Char(
        required=True,
        store=True,
    )
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        required=True,
    )
    birth_date = fields.Date(string="Date of Birth")
    age = fields.Integer(
        compute='_compute_age',
        store=True,
    )
    photo = fields.Binary("Photo", attachment=True)
    phone = fields.Char()
    email = fields.Char()
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Related Partner'
    )

    @api.model
    def create(self, vals):
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
        for record in self:
            if record.birth_date:
                record.age = relativedelta(fields.Date.today(), record.birth_date).years
            else:
                record.age = 0



