# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')

    state_id = fields.Many2one(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange')    