from odoo import fields, models


class UpdateDiscountDatesWizard(models.TransientModel):
    _name = 'caffeine_discount.update.dates.wizard'
    _description = 'Mass Reassign Doctor Wizard'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def update_dates(self):
        """
        Updates the start_date and end_date fields for the selected discounts.
        """
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            discounts = self.env['caffeine_discount.discount'].browse(
                active_ids)
            discounts.write({
                'start_date': self.start_date,
                'end_date': self.end_date,
            })
