##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class ProntoStockPicking(models.Model):
    _inherit = 'stock.picking'

    valor_declarado = fields.Monetary(string="Valor declarado", compute="_compute_valor_declarado")
    currency_id = fields.Many2one("res.currency", compute="_compute_valor_declarado", string="Currency", readonly=True, required=True)

    def _compute_valor_declarado(self):
        if self.sale_id:
            self.valor_declarado = self.sale_id.amount_untaxed
            self.currency_id = self.sale_id.currency_id
        else:
            self.currency_id = self.env.user.company_id.currency_id
    
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

    @api.multi
    def button_validate(self):
        result = super(ProntoStockPicking,self).button_validate()
        # solo en los movimientos de salida
        if (self.picking_type_id.code == 'outgoing'):
            # solo si tienen facturas asociadas.
            # osea que para tipo de venta 'sin factura' no aplica porque no se le asocia factura al movimiento
            # tampoco para las transferencia internas porque las operaciones son del tipo 'internal'
            for inv in self.invoice_ids:
                if (inv.type == 'out_invoice'):
                    # solo para las facturas (sin NC)
                    if (inv.state == 'draft'):
                        raise UserError("Este movimiento tiene al menos una factura asociada en estado borrador.")
        
        return result

    @api.model
    def _schedule_activity(self):

        model_stock_picking = self.env.ref('stock.model_stock_picking')
        asignada_a = self.env.user.company_id.usuario_responsable_reserva_stock_id
        # resumen
        summary = 'Contactar cliente por reserva de stock' 
        # tipo de actividad
        activity_type_id = self.env.ref('pronto.contactar_cliente_reserva_stock')

        vals = {
            'activity_type_id': activity_type_id.id,
            'date_deadline': fields.Date.today(),
            'summary': summary,
            'user_id': asignada_a.id,
            'res_id': self.id,
            'res_model_id': model_stock_picking.id,
            'res_model':  model_stock_picking.model
        }
    
        return self.env['mail.activity'].create(vals)