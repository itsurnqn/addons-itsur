# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from datetime import datetime

from odoo.osv import expression
from odoo.tools import float_is_zero, pycompat
from odoo.tools import float_compare, float_round, float_repr
from odoo.tools.misc import formatLang, format_date

import time
import math

class BoxBox(models.Model):
    _name = 'box.box'
    _description = 'Configuración de caja'

    name = fields.Char(string='Descripción', index=True, required=True, help="Una descripción interna de la caja.")
    journal_ids = fields.Many2many(
        'account.journal', 'box_journal_rel',
        'box_id', 'journal_id', string='Métodos de pago disponibles',
        domain="[('type', 'in', ['bank', 'cash'])]",)

    session_ids = fields.One2many('box.session', 'box_id', string='Sesiones')

    current_session_id = fields.Many2one('box.session', compute='_compute_current_session', string="Current Session")
    current_session_state = fields.Char(compute='_compute_current_session')
    # last_session_closing_cash = fields.Float(compute='_compute_last_session')
    # last_session_closing_date = fields.Date(compute='_compute_last_session')
    box_session_username = fields.Char(compute='_compute_current_session_user')
    box_session_state = fields.Char(compute='_compute_current_session_user')
    box_session_duration = fields.Char(compute='_compute_current_session_user')

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)


    cash_control = fields.Boolean(string='Has Cash Control',default=True,readonly=True)
    
    @api.depends('session_ids')
    def _compute_current_session_user(self):
        for box_box in self:
            session = box_box.session_ids.filtered(lambda s: s.state in ['opening_control', 'opened', 'closing_control'])
            if session:
                box_box.box_session_username = session[0].user_id.sudo().name
                box_box.box_session_state = session[0].state
                box_box.box_session_duration = (
                    datetime.now() - session[0].start_at
                ).days if session[0].start_at else 0
            else:
                box_box.box_session_username = False
                box_box.box_session_state = False
                box_box.box_session_duration = 0

    @api.depends('session_ids')
    def _compute_current_session(self):
        for box_box in self:
            session = box_box.session_ids.filtered(lambda r: r.user_id.id == self.env.uid and \
                not r.state == 'closed')
            # sessions ordered by id desc
            box_box.current_session_id = session and session[0].id or False
            box_box.current_session_state = session and session[0].state or False

    # Methods to open the POS
    @api.multi
    def open_ui(self):
        """ open the pos interface """
        self.ensure_one()
        # check all constraints, raises if any is not met
        # self._validate_fields(self._fields)
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url':   '/pos/web/',
        #     'target': 'self',
        # }

    @api.multi
    def open_session_cb(self):
        """ new session button

        create one if none exist
        access cash control interface if enabled or start a session
        """
        self.ensure_one()
        if not self.current_session_id:
            self.current_session_id = self.env['box.session'].create({
                'user_id': self.env.uid,
                'box_id': self.id
            })
            if self.current_session_id.state == 'opened':
                return self.open_ui()
            return self._open_session(self.current_session_id.id)
        return self._open_session(self.current_session_id.id)

    @api.multi
    def open_existing_session_cb(self):
        """ close session button

        access session form to validate entries
        """
        self.ensure_one()
        return self._open_session(self.current_session_id.id)

    def _open_session(self, session_id):
        return {
            'name': ('Session'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'box.session',
            'res_id': session_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
