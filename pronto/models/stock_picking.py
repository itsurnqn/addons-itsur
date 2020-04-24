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

    @api.multi
    def assign_numbers(self, estimated_number_of_pages, book):
        result = super(ProntoStockPicking,self).assign_numbers(estimated_number_of_pages, book)

        cantidad_renglones = self.env['stock.book'].browse(self.book_id.id).lines_per_voucher

        if (cantidad_renglones == 0):
            raise UserError("Debe configurar la cantidad de renglones para el talonario.")

        vouchers = self.env['stock.picking.voucher'].search([('picking_id','=',self.id)])

        for voucher in vouchers:
            # movimientos que todavía no tienen remitos asignados
            move_lines = self.env['stock.move.line'].search(['&',('picking_id','=',self.id),('picking_voucher_id','=',False)])
            renglon = 0
            for move in move_lines:
                move.write({'picking_voucher_id': voucher.id})
                renglon = renglon + 1
                if renglon >= cantidad_renglones:
                    break
            
        return result

    @api.multi
    def clean_voucher_data(self):
        move_lines = self.env['stock.move.line'].search([('picking_id','=',self.id)])
        for move in move_lines:
            move.picking_voucher_id = None
        result = super(ProntoStockPicking,self).clean_voucher_data()
