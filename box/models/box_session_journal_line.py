##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class BoxSessionJournalLine(models.Model):
    _name = 'box.session.journal.line'
    _description = 'box session journal line'
    # account.bank.statement.line

    @api.one
    def _compute_currency(self):
        self.currency_id = self.box_session_journal_id.journal_id.currency_id or self.company_id.currency_id

    name = fields.Char(string='Motivo', copy=False, readonly=True)
    ref = fields.Char(string='Descripción')
    
    account_payment_id = fields.Many2one(
        'account.payment', string='Pago asociado',
        help=".",
        # required=True,
        index=True)

    box_session_journal_id = fields.Many2one(
        'box.session.journal', string='Diario de la sesión',
        help=".",
        required=True,
        index=True)

    date = fields.Date(string='Fecha',required=True, default=lambda self: self._context.get('date', fields.Date.context_today(self)))

    amount = fields.Monetary(string='Monto')
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', string="Currency")
    partner_id = fields.Many2one('res.partner', string='Socio')
    
    company_id = fields.Many2one('res.company', related='box_session_journal_id.journal_id.company_id', string='Company', store=True, readonly=True,
        default=lambda self: self.env['res.company']._company_default_get('account.bank.statement'))

    anulado = fields.Boolean('Anulado',default=False)
    box_session_name = fields.Char(related="box_session_journal_id.box_session_id.name", string="Sesión de caja")        

    expense_id = fields.Many2one('hr.expense', string='Gasto')