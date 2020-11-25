##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.constrains('expense_line_ids', 'journal_id')
    def _check_journal(self):
        for sheet in self:
            journal_ids = sheet.expense_line_ids.mapped('journal_id')
            if len(journal_ids) > 1 or (len(journal_ids) == 1 and journal_ids != sheet.bank_journal_id):
                raise ValidationError(_('No es posible añadir gastos de diarios distintos.'))

    # @api.multi
    # def action_sheet_move_create(self):
        
    #     if self.env['hr.expense.sheet'].browse(16).expense_line_ids.mapped('invoice_id'):

    #     res = super(HrExpenseSheet,self).action_sheet_move_create()
    #     return res

    # @api.multi
    # def action_sheet_move_create(self):
    #     if any(sheet.state != 'approve' for sheet in self):
    #         raise UserError(_("You can only generate accounting entry for approved expense(s)."))

    #     if any(not sheet.journal_id for sheet in self):
    #         raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

    #     expense_line_ids = self.mapped('expense_line_ids')\
    #         .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.user.company_id.currency_id).rounding))
    #     res = expense_line_ids.action_move_create()

    #     if not self.accounting_date:
    #         self.accounting_date = self.account_move_id.date

    #     if self.payment_mode == 'own_account' and expense_line_ids:
    #         self.write({'state': 'post'})
    #     else:
    #         self.write({'state': 'done'})
    #     self.activity_update()
    #     return res