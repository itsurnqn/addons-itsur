##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    box_session_id = fields.Many2one('box.session', string='Sesión de caja', readonly="True", ondelete='Restrict', domain="[('state', '=', 'opened'),('user_id', '=', uid)]")

    @api.multi
    def get_journals_domain(self):
        domain = super(AccountPayment, self).get_journals_domain()
      
        journal_ids = self.env['box.session'].search([('state','=','opened'),('user_id','=',self.env.user.id)]).journal_ids.mapped('id')
        
        domain.append(('id', 'in', tuple(journal_ids)))

        # import pdb; pdb.set_trace()

        return domain