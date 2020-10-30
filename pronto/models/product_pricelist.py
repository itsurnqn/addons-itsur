##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    fixed_price = fields.Float(digits=dp.get_precision('Pricelist Fixed Price'))
