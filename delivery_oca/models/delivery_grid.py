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

    zona_oca_id = fields.Many2one('delivery.oca.zona','Zona OCA')

    # delivery_type = fields.Selection(related='carrier_id.delivery_type')
    margin = fields.Integer(related='carrier_id.margin')

    # @api.model
    # def create(self,values):
    #     res = super(PriceRule,self).create(values)
    #     import pdb; pdb.set_trace()
    #     return res