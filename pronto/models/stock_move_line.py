##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    picking_voucher_id = fields.Many2one(
        'stock.picking.voucher',
        'Remito',
        copy=False,
        ondelete='restrict',
    )