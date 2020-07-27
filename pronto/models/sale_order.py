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
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.free_qty, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message =  _('Pronto: Se intentan vender %s %s de %s pero solo existen %s %s disponibles en el depósito %s.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.free_qty, product.uom_id.name,self.order_id.warehouse_id.name)

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
