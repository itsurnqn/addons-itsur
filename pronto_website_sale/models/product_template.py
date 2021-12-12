# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        res['inventory_availability'] = 'always'
        return res

    @api.multi
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination, only_template)

        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            # combination_info['qty_available'] = product.qty_available
            # import pdb; pdb.set_trace()
            combination_info.update({
                'qty_available': product.qty_available,
            })            
            # import pdb; pdb.set_trace()
            
            # esto es para los packs. No lo puedo agregar en website_sale_product_pack porque el orden
            # de la ejecución de los métodos heredados hace que se pise (este metódo se ejecuta al final)
            # Probé haciendo que website_sale_product_pack dependa de pronto_website_sale pero no funcionó

            if product.pack_ok:
                combination_info.update({
                    'qty_available': product.qty_available,
                    'inventory_availability': 'always',
                    'pack_ok': product.pack_ok,
            })

        return combination_info
