##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class ProntoStockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_print_voucher(self):
        # import pdb; pdb.set_trace()
        '''This function prints the voucher'''
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', 'pronto.report_picking')],
            limit=1).report_action(self)
        return report