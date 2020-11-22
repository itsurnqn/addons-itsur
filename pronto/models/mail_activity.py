# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.one
    @api.depends('res_model', 'res_id')
    def _compute_res_url(self):
        self.res_url = '#id=%s&model=%s' % (self.res_id, self.res_model)

    res_url = fields.Char(string='Url documento relacionado', help='Link al documento relacionado.', compute=_compute_res_url)

