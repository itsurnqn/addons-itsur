##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    box_id = fields.Many2one('box.box', 
                    string='Caja', 
                    ondelete='Restrict')

    box_session_id = fields.Many2one('box.session', string='Sesión de caja', 
                    readonly="True", 
                    ondelete='Restrict')

    box_session_journal_line_ids = fields.One2many('box.session.journal.line', 'account_payment_id', string='Renglones de caja')

    @api.onchange('box_id','box_session_id')
    def onchange_box_session_id(self):
        if self.payment_type != 'transfer':
            self.journal_ids = self.box_session_id.journal_ids
            # import pdb; pdb.set_trace()
            if not self.box_session_id:
                raise UserError(_("Debe iniciar una sesión para poder operar con la caja '%s'." % self.box_id.name))

    @api.multi
    def cancel(self):
        super(AccountPayment,self).cancel()
        # import pdb; pdb.set_trace()

        # payment_type puede tener tres valores = transfer, inbound, outbound
        # transfer es, por ejemplo, un depósito de un cheque
        # los transfer no los registro en la caja
        if len(self) == 1 and self.payment_type == 'transfer':
            print("nada que anular. Es una transferencia")
        else:
            default_box_id = self.env.user.default_box_id

            session_actual = self.env['box.session'].search([('state','=','opened'),('box_id','=',default_box_id.id)])

            if not session_actual:            
                raise UserError(_("Debe iniciar una sesión de la caja '%s', para poder cancelar el recibo." % default_box_id.name))
            else:
                # si se cancela antes de validar el recibo, puede pasar que no tenga renglon de pago (para recibos y para OP)
                # en este caso self.id = 0. entonces solo debo cancelar la linea de caja en caso que exista el renglón de pago

                # el metodo cancel se invoca desde el metodo cancel del account_payment_group de adhoc.
                # y lo invoca así: rec.payment_ids.cancel() . eso quiere decir que como self de este metodo recibe
                # algo del tipo account_payment(). que es así account_payment(n) si el recibo tiene n medios de pago.
                
                # si no tiene renglones, no hay nada que anular en la caja
                if len(self) > 0:
                    
                    for rec in self:
                        # solo si el renglon está validado se tiene que anular en la caja
                        if (rec.payment_group_id.state == 'posted'):
                            
                            renglones = self.env['box.session.journal.line'].search([('account_payment_id','=',rec.id), ('anulado','=',False)])

                            # analizar que pasa cuando se está anulando un recibo de un turno anterior ...
                            # me tengo que asegurar que se registre en la sesión actual            
                            # busco el diario que corresponda según lo que se este anulando (self.journal_id)            
                            # busco la linea (box.session.journal) que corresponde para el diario, dentro de la sesión actual.                         
                            box_session_journal_id = self.env['box.session.journal'].search([('journal_id','=',rec.journal_id.id),('box_session_id.id','=',session_actual.id)])

                            if not box_session_journal_id:
                                raise UserError(_("El medio de pago '%s', no está habilitado para la caja actual '%s'." % (rec.journal_id.name,default_box_id.name)))
                            
                            # renglones siempre debería tener un solo registro. 
                            # por las dudas los controlo
                            if len(renglones) > 1:
                                raise UserError(_("Error"))
                            
                            for renglon_caja in renglones:
                                if (renglon_caja.ref):
                                    ref = renglon_caja.ref
                                else:
                                    ref = ''

                                vals = {
                                    'name': renglon_caja.display_name, 
                                    'amount': -renglon_caja.amount, 
                                    'partner_id': renglon_caja.partner_id.id,
                                    'ref': ref + ' - Motivo Cancelación: ' + rec.payment_group_id.cancel_reason_note,
                                    'account_payment_id': renglon_caja.account_payment_id.id,
                                    'box_session_journal_id': box_session_journal_id.id,
                                    'anulado': True
                                }

                                self.env['box.session.journal.line'].create(vals)

                                renglon_caja.anulado = True

                        else:
                            print("No tiene que anular en la caja 1.")
                        
                else:
                    print("No tiene que anular en la caja 2.")
