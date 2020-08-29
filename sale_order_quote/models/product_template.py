##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    registrar_novedad_presupuesto = fields.Boolean("Registrar novedad presupuesto", default=True)