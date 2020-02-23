##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError

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
                else:
                        amount = rec2.amount                

                vals = {
                    'name': rec2.display_name, 
                    'amount': amount, 
                    'partner_id': self.partner_id.id,
                    # 'ref': self.pos_session_id.name
                    'account_payment_id': rec2.id,
                    'box_session_journal_id': box_session_journal_id.id
                }

                self.env['box.session.journal.line'].create(vals)
