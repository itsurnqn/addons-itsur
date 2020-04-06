##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from ast import literal_eval
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        # CUIDADO: esto depende de purchase_ux de adhoc. porque agrega la relacion de la OC con las facturas.
        for rec in self:
            if not rec.purchase_order_ids:
                raise UserError("Debe informar las OC asociadas.")         

        res = super(AccountInvoice, self).action_invoice_open()

      

    # @api.multi
    # def action_invoice_open(self):
    #     # lots of duplicate calls to action_invoice_open, so we remove those already open
    #     to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
    #     if to_open_invoices.filtered(lambda inv: not inv.partner_id):
    #         raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
    #     if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
    #         raise UserError(_("Invoice must be in draft state in order to validate it."))
    #     if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
    #         raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
    #     if to_open_invoices.filtered(lambda inv: not inv.account_id):
    #         raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
    #     to_open_invoices.action_date_assign()
    #     to_open_invoices.action_move_create()
    #     return to_open_invoices.invoice_validate()