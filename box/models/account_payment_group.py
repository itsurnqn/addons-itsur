##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    def _get_default_box_session_id(self):

        usuario_actual_id = self.env.uid        
        
        return self.env['box.session'].search(['&',('state','=','opened'),('user_id', '=', usuario_actual_id)]).id

    box_session_id = fields.Many2one('box.session', 
                    string='Sesión de caja', 
                    ondelete='Restrict',
                    domain="[('state', '=', 'opened'),('user_id', '=', uid)]",
                    default=_get_default_box_session_id)

    @api.multi
    def post(self):
        super(AccountPaymentGroup, self).post()
        for rec in self:
            for rec2 in rec.payment_ids.filtered(lambda x: x.state == 'posted'):
                rec2.box_session_id = self.box_session_id

                box_session_journal_id = self.env['box.session.journal'].search(['&',('box_session_id','=',self.box_session_id.id),('journal_id','=',rec2.journal_id.id)])
                #import pdb;pdb.set_trace()

                

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

                    # if rec2.journal_id.type == 'bank':                        
                    # else:
                    #     ref = rec2.display_name

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

                self.env['box.session.journal.line'].create(vals)