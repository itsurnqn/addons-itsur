##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_delivery_line(self, carrier, price_unit):

        sol = super(SaleOrder,self)._create_delivery_line(carrier, price_unit)

        # sol = sale order line
        # carrier.margin = 10 %
        # purchase_price = price_unit / 1,10
        if carrier.margin:
            sol.purchase_price = price_unit / (carrier.margin/100 + 1)
        else:
            sol.purchase_price = price_unit

        if sol.product_id.description_sale:
            sol.name = sol.product_id.description_sale
        
        return sol