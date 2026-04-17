from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_web_property_occupancy_warning = fields.Boolean(
        string='Aviso de ocupación desde web'
    )

    x_web_property_occupancy_message = fields.Text(
        string='Mensaje de ocupación web'
    )
