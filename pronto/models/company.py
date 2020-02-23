# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    stock_delivery_note = fields.Text(
        string='Nota Remito', 
        help="Texto que se imprime en el remito")