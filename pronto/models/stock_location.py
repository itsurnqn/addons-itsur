from odoo import api, fields, models

class StockLocation(models.Model):
    _inherit = "stock.location"

    computar_stock_disponible = fields.Boolean("Computar como stock disponible",default=True)