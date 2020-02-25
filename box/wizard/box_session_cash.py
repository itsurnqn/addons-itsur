from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BoxSessionCashIn(models.TransientModel):
    _name = 'box.session.cash.in'
    _description = 'Ingreso de efectivo'

    amount = fields.Float(string='Amount', digits=0, required=True)

    box_session_id = fields.Many2one('box.session',string='Sesión')

    description = fields.Char(string='Motivo')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            BoxSessionCashIn, self).default_get(field_names)
        defaults['box_session_id'] = self.env.context['active_id']
        return defaults

    def do_cash_in(self):
        box_session_journal_id = self.env['box.session.journal'].search(['&',('box_session_id','=',self.box_session_id.id),('journal_id','=',self.box_session_id.cash_journal_id.id)])
        #import pdb;pdb.set_trace()

        vals = {
            'ref': self.description, 
            'amount': self.amount, 
            # 'partner_id': self.partner_id.id,
            # 'ref': self.box_session_id.name,
            # 'account_payment_id': rec2.id,
            'box_session_journal_id': box_session_journal_id.id
        }

        self.env['box.session.journal.line'].create(vals)        

class BoxSessionCashOpen(models.TransientModel):
    _name = 'box.session.cash.open'
    _description = 'Informar saldo inicial'

    amount = fields.Float(string='Amount', digits=0, required=True)

    box_session_id = fields.Many2one('box.session',string='Sesión')

    description = fields.Char(string='Motivo')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            BoxSessionCashOpen, self).default_get(field_names)
        defaults['box_session_id'] = self.env.context['active_id']
        return defaults

    def do_box_open(self):
        box_session_journal_id = self.env['box.session.journal'].search(['&',('box_session_id','=',self.box_session_id.id),('journal_id','=',self.box_session_id.cash_journal_id.id)]).id

        self.env['box.session.journal'].search([('id','=',box_session_journal_id)]).write({'balance_start':self.amount})

class BoxSessionCashOut(models.TransientModel):
    _name = 'box.session.cash.out'
    _description = 'Retiro de efectivo'

    amount = fields.Float(string='Amount', digits=0, required=True)

    box_session_id = fields.Many2one('box.session',string='Sesión')

    description = fields.Char(string='Motivo')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            BoxSessionCashOut, self).default_get(field_names)
        defaults['box_session_id'] = self.env.context['active_id']
        return defaults

    def do_cash_out(self):
        box_session_journal_id = self.env['box.session.journal'].search(['&',('box_session_id','=',self.box_session_id.id),('journal_id','=',self.box_session_id.cash_journal_id.id)])
        #import pdb;pdb.set_trace()

        vals = {
            'ref': self.description, 
            'amount': - self.amount, 
            # 'partner_id': self.partner_id.id,
            # 'ref': self.box_session_id.name,
            # 'account_payment_id': rec2.id,
            'box_session_journal_id': box_session_journal_id.id
        }

        self.env['box.session.journal.line'].create(vals)
    
class BoxSessionCashClose(models.TransientModel):
    _name = 'box.session.cash.close'
    _description = 'Informar saldo final'

    amount = fields.Float(string='Amount', digits=0, required=True)

    box_session_id = fields.Many2one('box.session',string='Sesión')

    description = fields.Char(string='Motivo')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            BoxSessionCashClose, self).default_get(field_names)
        defaults['box_session_id'] = self.env.context['active_id']
        return defaults

    def do_box_close(self):
        box_session_journal_id = self.env['box.session.journal'].search(['&',('box_session_id','=',self.box_session_id.id),('journal_id','=',self.box_session_id.cash_journal_id.id)]).id

        self.env['box.session.journal'].search([('id','=',box_session_journal_id)]).write({'balance_end_real':self.amount})