##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    box_session_id = fields.Many2one('box.session', string='Sesión de caja', readonly="True", ondelete='Restrict', domain="[('state', '=', 'opened'),('user_id', '=', uid)]")

    box_session_journal_line_id = fields.Many2one('box.session.journal.line')

    @api.multi
    def get_journals_domain(self):
        domain = super(AccountPayment, self).get_journals_domain()
      
        journal_ids = self.env['box.session'].search([('state','=','opened'),('user_id','=',self.env.user.id)]).journal_ids.mapped('id')
        
        domain.append(('id', 'in', tuple(journal_ids)))

        # import pdb; pdb.set_trace()

        return domain

    @api.multi
    def cancel(self):
        super(AccountPayment,self).cancel()

        # tengo que controlar que la caja este abierta.
        session_actual = self.env['box.session'].search([('state','=','opened'),('user_id','=',self.env.user.id)])

        if not session_actual:
            raise UserError(_("Debe iniciar una sesión de caja para poder cancelar el recibo."))
        else:
            # si se cancela antes de validar el recibo, puede pasar que no tenga renglon de pago (para recibos y para OP)
            # en este caso self.id = 0. entonces solo debo cancelar la linea de caja en caso que exista el renglón de pago
            if (self.id != 0):
                # solo si el recibo está validado se tiene que anular en la caja
                if (self.payment_group_id.state == 'posted'):

                    print("Anula en la caja")

                    # renglon_caja = self.env['box.session.journal.line'].search([('account_payment_id','=',self.id)])
                    renglon_caja = self.env['box.session.journal.line'].browse(self.box_session_journal_line_id.id)

                    # analizar que pasa cuando se está anulando un recibo de un turno anterior ...
                    # me tengo que asegurar que se registre en la sesión actual            
                    # busco el diario que corresponda según lo que se este anulando (self.journal_id)            
                    # busco la linea (box.session.journal) que corresponde para el diario, dentro de la sesión actual. 
                    
                    box_session_journal_id = self.env['box.session.journal'].search([('journal_id','=',self.journal_id.id),('box_session_id.id','=',session_actual.id)])
                    # box_session_journal_id = self.env['box.session.journal'].browse(self.box_session_journal_line_id.box_session_journal_id.id)

                    # import pdb; pdb.set_trace()

                    if (renglon_caja.ref):
                        ref = renglon_caja.ref
                    else:
                        ref = ''

                    vals = {
                        'name': renglon_caja.display_name, 
                        'amount': -renglon_caja.amount, 
                        'partner_id': renglon_caja.partner_id.id,
                        'ref': ref + ' - Cancelación',
                        'account_payment_id': renglon_caja.account_payment_id.id,
                        'box_session_journal_id': box_session_journal_id.id
                    }

                    self.env['box.session.journal.line'].create(vals)
                else:
                    print("No tiene que anular en la caja 1.")
            else:
                print("No tiene que anular en la caja 2.")
