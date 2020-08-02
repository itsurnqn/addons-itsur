# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def invoice_line_create_vals(self, invoice_id, qty):
        self.mapped(
            'move_ids'
        ).filtered(
            lambda x: not x.invoice_line_id and
            not x.location_dest_id.scrap_location and
            x.location_dest_id.usage == 'customer'
        ).mapped(
            'picking_id'
        ).write({'invoice_ids': [(4, invoice_id)]})
        return super(SaleOrderLine, self).invoice_line_create_vals(invoice_id,
                                                                   qty)

    # con este desactivo el chequeo que hace el CORE
    # tome la idea del modulo sale_disable_inventory_check
    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        return {}

    @api.onchange('product_id')
    def _onchange_product_id_uom_check_availability_ux(self):
        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            self.product_uom = self.product_id.uom_id
        self._onchange_product_id_check_availability_ux()

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability_ux(self):        
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            warehouse_id = self.order_id.warehouse_id.id
            product = self.product_id.with_context(
                warehouse=warehouse_id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.free_qty, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message =  _('Pronto: Se intentan vender %s %s de\n %s\n pero solo existen %s %s disponibles (A mano - Reservado) en el depósito:\n %s.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.free_qty, product.uom_id.name,self.order_id.warehouse_id.name)

                    # warehouse_ids = self.env['stock.warehouse'].search([('id','!=',warehouse_id)])
                    warehouse_ids = self.env['stock.warehouse'].search([])

                    message += ('\n\n Detalle del disponible por Depósito \n')

                    for wh in warehouse_ids:
                        product = self.product_id.with_context(
                            warehouse=wh.id,
                            lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
                        )
                        message += ('\n %s: %s %s' % (wh.name,product.free_qty,self.product_uom.name))    

                    message += ('\n\n El total disponible en todos los depósitos es de %s %s' % (self.free_qty_today,self.product_uom.name))
                    
                    warning_mess = {
                        'title': _('No hay suficiente stock!'),
                        'message' : message
                    }
                    return {'warning': warning_mess}

        # return res
        return {}
        
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        # import pdb; pdb.set_trace()
        if self.env.user.sale_journal_id:
            res['journal_id'] = self.env.user.sale_journal_id.id
        return res

    @api.multi
    def _action_confirm(self):
        super(SaleOrder, self)._action_confirm()
        for picking in self.picking_ids:
            self.env['procurement.group'].run_smart_scheduler(picking.id)
