from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    exchange_rate = fields.Float(readonly=False)

    @api.onchange('exchange_rate')
    def exchange_rate_change(self):
        for rec in self:
            rec.amount_company_currency = rec.exchange_rate * rec.amount
    