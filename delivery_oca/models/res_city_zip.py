##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models

class DeliveryCarrier(models.Model):
    _inherit = 'res.city.zip'

    zona_oca_id = fields.Many2one('delivery.oca.zona','Zona OCA')