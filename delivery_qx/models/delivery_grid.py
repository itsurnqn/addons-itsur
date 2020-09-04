##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError

class PriceRule(models.Model):
    _inherit = "delivery.price.rule"

    zona_qx_id = fields.Many2one('delivery.qx.zona','Zona qx')

    delivery_type = fields.Selection(related='carrier_id.delivery_type')   