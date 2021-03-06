# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    stock_delivery_note = fields.Text(
        string='Nota Remito', 
        help="Texto que se imprime en el remito")

    product_pricelist_cost_id = fields.Many2one('product.pricelist',string="Lista de precio de costo",default=3)

    usuario_responsable_reserva_stock_id = fields.Many2one('res.users',string="Resp. reservas de stock")

    usuario_responsable_actualizacion_costo_id = fields.Many2one('res.users',string="Resp. actualización de tarifa de costo")