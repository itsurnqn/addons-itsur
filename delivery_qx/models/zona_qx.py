##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models

class ZonaQx(models.Model):
    _name = 'delivery.qx.zona'
    _description = "Zona QX"
    _rec_name = "name"

    name = fields.Char('Zona qx')
    codigo = fields.Integer('Código')