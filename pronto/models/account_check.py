from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config

class AccountCheck(models.Model):
    _inherit = 'account.check'

    no_a_la_orden = fields.Boolean('No a la orden?',default=False)