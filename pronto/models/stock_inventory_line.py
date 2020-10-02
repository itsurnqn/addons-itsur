from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    diff_real_theo_qty = fields.Float(
        'Diferencia', compute='_compute_diff_qty',
        digits=dp.get_precision('Product Unit of Measure'), readonly=True, store=True)

    @api.one
    @api.depends('product_qty', 'theoretical_qty')
    def _compute_diff_qty(self):
        self.diff_real_theo_qty = self.product_qty - self.theoretical_qty