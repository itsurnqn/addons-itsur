from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BoxSessionCashExpense(models.TransientModel):
    _name = 'box.session.cash.expense'
    _description = 'Gasto'

    box_session_id = fields.Many2one('box.session',string='Sesión')

    name = fields.Char(string='Descripción')
    unit_amount = fields.Float(string='Importe', digits=0, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, default=lambda self: self.env.user.company_id.currency_id)
    product_id = fields.Many2one('product.product', string='Producto/Servicio', required=True, domain=[('can_be_expensed', '=', True)])

    adjunto = fields.Binary("Comprobante")
    file_name = fields.Char("File Name")

    @api.model
    def default_get(self, field_names):
        defaults = super(BoxSessionCashExpense, self).default_get(field_names)
        defaults['box_session_id'] = self.env.context['active_id']
        return defaults

    def do_cash_out(self):
        
        if self.unit_amount == 0:
            raise UserError(_('El importe no puede ser cero.'))

        vals0 = {
            'name': self.name,
            'unit_amount' : self.unit_amount,
            'product_id': self.product_id.id,
            # 'product_uom'
            'quantity': 1,
            'employee_id': self.box_session_id.user_id.employee_ids.id,
            'payment_mode': "company_account",
            'journal_id': self.box_session_id.cash_journal_id.id
        }

        expense_id = self.env['hr.expense'].create(vals0)

        # Adjunto
        if self.adjunto:
            nombre_adjunto = self.file_name
            IrAttachment = self.env['ir.attachment']
            data_attach = {
                'name': nombre_adjunto,
                'datas': self.adjunto,
                'type': 'binary',
                'datas_fname': nombre_adjunto,
                'description': nombre_adjunto,
                'res_model': "hr.expense",
                'res_id': expense_id.id,
            }
            new_attachment = IrAttachment.create(data_attach)

            data_attach2 = {
                'name': nombre_adjunto,
                'datas': self.adjunto,
                'type': 'binary',
                'datas_fname': nombre_adjunto,
                'description': nombre_adjunto,
                'res_model': "box.session",
                'res_id': self.box_session_id.id,
            }
            new_attachment2 = IrAttachment.create(data_attach2)

        box_session_journal_id = self.env['box.session.journal'].search(['&',('box_session_id','=',self.box_session_id.id),('journal_id','=',self.box_session_id.cash_journal_id.id)])
        #import pdb;pdb.set_trace()

        vals = {
            'ref': self.name, 
            'amount': - self.unit_amount, 
            # 'partner_id': self.partner_id.id,
            # 'ref': self.box_session_id.name,
            # 'account_payment_id': rec2.id,
            'box_session_journal_id': box_session_journal_id.id,
            'expense_id': expense_id.id
        }

        new_box_session_journal_line_id = self.env['box.session.journal.line'].create(vals)

        expense_id.box_session_journal_line_id = new_box_session_journal_line_id