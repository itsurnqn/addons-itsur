##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    box_session_journal_line_id = fields.Many2one(
        'box.session.journal.line', string='Linea',
        help=".",
        # required=True,
        index=True)

    box_id = fields.Many2one(string="Caja", related="box_session_journal_line_id.box_session_journal_id.box_session_id.box_id")
    # journal_id = fields.Many2one(string="Diario", related="box_session_journal_line_id.box_session_journal_id.journal_id")
    journal_id = fields.Many2one('account.journal', string="Diario")

    unit_amount = fields.Float(track_visibility=True)

    @api.multi
    def action_submit_expenses(self):
        res = super(HrExpense,self).action_submit_expenses()
        # import pdb; pdb.set_trace()
        res["context"]["default_bank_journal_id"] = 0
        return res

    @api.multi
    def unlink(self):
        for expense in self:
            if expense.box_id:
                raise UserError(_('No se puede suprimir un gasto que ingreso desde una caja.'))
        super(HrExpense, self).unlink()