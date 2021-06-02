from odoo import fields, api, models

class StockPrintStockVoucher(models.TransientModel):
    _inherit = 'stock.print_stock_voucher'

    @api.onchange('book_id', 'picking_id')
    def get_estimated_number_of_pages(self):
        lines_per_voucher = self.lines_per_voucher
        if lines_per_voucher == 0:
            self.estimated_number_of_pages = 1
            return

        operations = len(self.picking_id.move_ids_without_package)
        estimated_number_of_pages = int(
            -(-float(operations) // float(lines_per_voucher)))
        self.estimated_number_of_pages = estimated_number_of_pages    