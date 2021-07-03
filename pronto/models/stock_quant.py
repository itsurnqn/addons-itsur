from odoo import fields, api, models

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    categ_id = fields.Many2one(related="product_tmpl_id.categ_id", string="Categoría de producto", store=True)

    parent_categ_id = fields.Many2one(related="product_tmpl_id.categ_id.parent_id", string="Categoría Padre de producto", store=True)