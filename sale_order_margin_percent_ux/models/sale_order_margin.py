# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    percent = fields.Float(
        string='Porcentaje',
        compute='_compute_percent',
        digits=(16, 2),
        )

    @api.depends('margin', 'amount_untaxed')
    def _compute_percent(self):
        for order in self:
            purchase_price_total = 0
            for line in order.order_line:
                purchase_price_total += line.purchase_price
            if order.margin and purchase_price_total:
                # caso Pronto
                order.percent = (order.margin / purchase_price_total) * 100
                # como lo hace OCA
                # order.percent = (order.margin / order.amount_untaxed) * 100