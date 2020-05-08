##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    sale_journal_id = fields.Many2one('account.journal',
            'Diario de facturación por defecto', 
            copy=False,
            ondelete='restrict',
            domain=[('type','=','sale')])