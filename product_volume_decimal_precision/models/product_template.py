# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, fields
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    volume = fields.Float(
        'Volume', compute='_compute_volume', digits=dp.get_precision('Stock Volume'), inverse='_set_volume',
        help="The volume in m3.", store=True)    