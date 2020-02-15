##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    @api.multi
    def payment_print(self):
        report = self.env['ir.actions.report']._get_report_from_name('pronto.report_payment_group')
        return report.report_action(docids=self)