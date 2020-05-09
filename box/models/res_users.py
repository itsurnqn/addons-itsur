from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    default_box_id = fields.Many2one(
        'box.box', 
        string='Caja por defecto',
        help="Caja por defecto para el usuario.")