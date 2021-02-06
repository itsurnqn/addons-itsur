##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

class ProductPricelistItemHistory(models.Model):
    _name = 'product.pricelist.item.history'
    _description = 'Histórico de items de tarifas'
    _rec_name = 'product_tmpl_id'

    product_tmpl_id = fields.Many2one('product.template', 'Producto')
    fixed_price = fields.Float('Precio fijo', digits=dp.get_precision('Product Price'))
    pricelist_item_id = fields.Many2one('product.pricelist.item', 'Item de tarifa')
    pricelist_id = fields.Many2one(string="Tarifa", related="pricelist_item_id.pricelist_id")

    @api.model
    def _inicializar_modelo(self):
        # se corre por única vez en la creación de la funcionalidad
        if not self.env["product.pricelist.item.history"].search([]):
            item_history = self.env["product.pricelist.item.history"]
            for item in self.env["product.pricelist.item"].search([('pricelist_id','=',2)]):
                item_history.create({
                    'product_tmpl_id': item.product_tmpl_id.id,
                    'fixed_price': item.fixed_price,
                    'pricelist_item_id': item.id
                })

        return