from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    exchange_rate = fields.Float(readonly=False)

    no_a_la_orden = fields.Boolean('No a la orden?',default=False)
    
    @api.onchange('exchange_rate')
    def exchange_rate_change(self):
        for rec in self:
            rec.amount_company_currency = rec.exchange_rate * rec.amount

    @api.multi
    def create_check(self, check_type, operation, bank):
        self.ensure_one()
        res = super(AccountPayment, self).create_check(check_type, operation, bank)        
        # import pdb; pdb.set_trace()
        res.no_a_la_orden = self.no_a_la_orden
        return(res)

    # @api.multi
    # def create_check(self, check_type, operation, bank):
    #     self.ensure_one()

    #     check_vals = {
    #         'bank_id': bank.id,
    #         'owner_name': self.check_owner_name,
    #         'owner_vat': self.check_owner_vat,
    #         'number': self.check_number,
    #         'name': self.check_name,
    #         'checkbook_id': self.checkbook_id.id,
    #         'issue_date': self.check_issue_date,
    #         'type': self.check_type,
    #         'journal_id': self.journal_id.id,
    #         'amount': self.amount,
    #         'payment_date': self.check_payment_date,
    #         'currency_id': self.currency_id.id,
    #         'amount_company_currency': self.amount_company_currency,
    #     }

    #     check = self.env['account.check'].create(check_vals)
    #     self.check_ids = [(4, check.id, False)]
    #     check._add_operation(
    #         operation, self, self.partner_id, date=self.payment_date)
    #     return check