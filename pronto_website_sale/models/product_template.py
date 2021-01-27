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