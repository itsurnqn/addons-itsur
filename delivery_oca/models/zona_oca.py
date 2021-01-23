##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models

class ZonaQx(models.Model):
    _name = 'delivery.oca.zona'
    _description = "Zona OCA"
    _rec_name = "name"

    name = fields.Char('Zona OCA')
    codigo = fields.Integer('Código')