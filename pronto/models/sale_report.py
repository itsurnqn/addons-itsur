# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class SaleReport(models.Model):
    _inherit = 'sale.report'


    costo_total_pesos = fields.Float('Costo total en pesos', readonly=True)
    precio_total_pesos = fields.Float('Precio total en pesos', readonly=True)
    porcentaje = fields.Float('Porcentaje', readonly=True)

    tag_ids = fields.Many2many(related="order_id.tag_ids",string = "Etiquetas")

    # este no hace falta. El filtro que usa (product_id not null) para que no se muestren las seccione
    # display_type = fields.Selection([
    #     ('line_section', "Section"),
    #     ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['costo_total_pesos'] = ', l.costo_total_pesos as costo_total_pesos'
        fields['precio_total_pesos'] = ', l.precio_total_pesos as precio_total_pesos'
        fields['porcentaje'] = ', CASE WHEN l.costo_total_pesos > 0 and l.precio_total_pesos > 0 THEN  (l.precio_total_pesos / l.costo_total_pesos - 1) * 100 ELSE 0 END as porcentaje'

# porcentaje
        groupby += ', l.costo_total_pesos, l.precio_total_pesos, porcentaje'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
