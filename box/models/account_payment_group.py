##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    def _get_default_box_id(self):
        return self.env.user.default_box_id.id

    box_id = fields.Many2one('box.box', 
        string='Caja', 
        ondelete='Restrict',
        default=_get_default_box_id,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    box_session_id = fields.Many2one('box.session', 
        string='Sesión de caja', 
        ondelete='Restrict',
        domain="['&',('box_id','=',box_id),('state','=','opened')]",
        readonly=True,
        states={'draft': [('readonly', False)]},        
    )

    # para mostrar los renglones de caja asociados en el recibo
    box_session_journal_line_ids = fields.One2many(related='payment_ids.box_session_journal_line_ids', string='Renglones de caja')

    @api.onchange('box_id')
    def _onchange_box_id(self):
        # si el usuario cambia la caja, que cargue la sesion activa para esa caja y que blanquee la grilla de pagos
        self.box_session_id = self.env['box.session'].search(['&',('box_id','=',self.box_id.id),('state','=','opened')])
        self.payment_ids = False

    @api.multi
    def post(self):
        super(AccountPaymentGroup, self).post()
        for rec in self:
            
            # verificar que la sesión de caja esté abierta.
            # ej para los casos en los que el recibo quedó en borrador con una sesión antigua
            
            # cuando el cobro/pago se genera desde la conciliacion, la sesion viene en blanco.
            # parece que no se ejecuta el _onchange_box_id
            if (not rec.box_session_id):                
                rec.box_session_id = self.env['box.session'].search(['&',('box_id','=',rec.box_id.id),('state','=','opened')])

            if (rec.box_session_id.state != 'opened'):
                raise UserError(_("La sesión de caja esta cerrada. %s") % rec.box_session_id.display_name)
            else:
                for rec2 in rec.payment_ids.filtered(lambda x: x.state in ('posted','reconciled')):
                    rec2.box_id = rec.box_id
                    rec2.box_session_id = self.box_session_id
                    
                    box_session_journal_id = self.env['box.session.journal'].search(['&',('box_session_id','=',self.box_session_id.id),('journal_id','=',rec2.journal_id.id)])

                    if self.partner_type == 'supplier':
                        amount = - rec2.amount
                        ref = 'pago a proveedor'
                    else:
                        amount = rec2.amount                

                    inbound_payment_method_codes = rec2.journal_id.inbound_payment_method_ids.mapped('code')

                    if 'received_third_check' in inbound_payment_method_codes:
                        # cheque de tercero
                        ref = rec2.check_bank_id.name + ' - ' + rec2.check_payment_date.strftime("%m/%d/%Y")
                    elif 'electronic' in inbound_payment_method_codes:
                        # transferencia bancaria
                        ref = 'Transferencia '
                    elif 'withholding' in inbound_payment_method_codes:
                        # retenciones
                        ref = rec2.tax_withholding_id.name + ' - ' + rec2.withholding_number
                    elif 'inbound_credit_card' in inbound_payment_method_codes:
                        # tarjeta crédito
                        ref = "Lote: " + str(rec2.nro_lote) + " - " + "Cupón: " + rec2.nro_cupon
                    elif 'outbound_debit_card' in inbound_payment_method_codes:
                        # tarjeta débito
                        ref = ''
                    else:
                        ref = ''
                    
                    if rec2.communication != '.' and rec2.communication:
                        ref = ref + ' - ' + rec2.communication

                    vals = {
                        'name': rec2.display_name, 
                        'amount': amount, 
                        'partner_id': self.partner_id.id,
                        'ref': ref,
                        'account_payment_id': rec2.id,
                        'box_session_journal_id': box_session_journal_id.id
                    }                  
                    
                    rec2.box_session_journal_line_id = self.env['box.session.journal.line'].create(vals)