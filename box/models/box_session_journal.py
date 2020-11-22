##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class BoxSessionJournal(models.Model):
    _name = 'box.session.journal'
    _description = 'Detalle del medio de pago'
    # account.bank.statement

    @api.one
    @api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real')
    def _end_balance(self):
        self.total_entry_encoding = sum([line.amount for line in self.line_ids])
        self.balance_end = self.balance_start + self.total_entry_encoding
        self.difference = self.balance_end_real - self.balance_end
        self.total_entry_encoding_in = sum([line.amount for line in self.line_ids.filtered(lambda x: x.amount > 0)])
        self.total_entry_encoding_out = sum([line.amount for line in self.line_ids.filtered(lambda x: x.amount < 0)])

    @api.model
    def _default_opening_balance(self):
        #Search last bank statement and set current opening balance as closing balance of previous one
        # journal_id = self._context.get('default_journal_id', False) or self._context.get('journal_id', False)
        # if journal_id:
        #     return self._get_opening_balance(journal_id)
        
        return 0

    @api.one
    @api.depends('journal_id')
    def _compute_currency(self):
        self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
   
    name = fields.Char(string='Reference', copy=False, readonly=True)

    box_session_id = fields.Many2one(
        'box.session', string='Sesión',
        help=".",
        required=True,
        index=True)

    journal_id = fields.Many2one(
        'account.journal', string='Diario',
        help=".",
        required=True,
        index=True)

    line_ids = fields.One2many('box.session.journal.line', 'box_session_journal_id', string='Detalle movimientos', copy=True)

    balance_start = fields.Monetary(string='Saldo inicial', default=_default_opening_balance)
    balance_end = fields.Monetary('Saldo final calculado', compute='_end_balance', store=True, help='Balance as calculated based on Opening Balance and transaction lines')
    total_entry_encoding = fields.Monetary('Transacciones', compute='_end_balance', store=True, help="Total of transaction lines.")
    balance_end_real = fields.Monetary('Saldo final')
    difference = fields.Monetary(compute='_end_balance', store=True, help="Difference between the computed ending balance and the specified ending balance.")

    currency_id = fields.Many2one('res.currency', compute='_compute_currency', oldname='currency', string="Moneda")

    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', store=True, readonly=True,
        default=lambda self: self.env['res.company']._company_default_get('account.bank.statement'))

    date = fields.Date(required=True, index=True, copy=False, default=fields.Date.context_today, string="Fecha")

    total_entry_encoding_in = fields.Monetary('Ingresos', compute='_end_balance', store=True)
    total_entry_encoding_out = fields.Monetary('Egresos', compute='_end_balance', store=True)