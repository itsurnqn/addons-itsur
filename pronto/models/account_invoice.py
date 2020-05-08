##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from ast import literal_eval
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_journal(self):
        res = super(AccountInvoice, self)._default_journal()        
        if res.type == 'sale':
            res = self.env.user.sale_journal_id
        import pdb; pdb.set_trace()
        return(res)