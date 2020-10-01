# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
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

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        warehouse_id = self.route_id.rule_ids.picking_type_id.warehouse_id
        if not warehouse_id:
            warehouse_id = self.order_id.warehouse_id

        if self.product_id.type == 'service' and self.product_id.pack_ok:
            # es un pack. tengo que controlar stock de cada uno de los componentes
            for line in self.product_id.pack_line_ids:
                product_id = line.product_id
                product = product_id.with_context(
                    warehouse=warehouse_id.id,
                    lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
                )
                product_qty = self.product_uom._compute_quantity(self.product_uom_qty * line.quantity, self.product_id.uom_id)
                if float_compare(product.free_qty, product_qty, precision_digits=precision) == -1:
                    is_available = self._check_routing()
                    if not is_available:
                        message = 'No existe suficiente stock disponible del producto: \n{} \n\npara completar {} {} del pack: \n{} \n\nen el depósito: \n{}'.format(
                            product_id.name,
                            self.product_uom_qty,
                            self.product_uom.name,
                            self.product_id.name,
                            warehouse_id.name
                        )
                        
                        warning_mess = {
                            'title': _('No hay suficiente stock!'),
                            'message' : message
                        }
                        return {'warning': warning_mess}
                
        elif self.product_id.type == 'product':            

            product = self.product_id.with_context(
                warehouse=warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            # import pdb; pdb.set_trace()
            if float_compare(product.free_qty, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message =  _('Pronto: Se intentan vender %s %s de\n %s\n pero solo existen %s %s disponibles (A mano - Reservado) en el depósito:\n %s.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.free_qty, product.uom_id.name,warehouse_id.name)

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

    def _get_default_carrier(self):
        return self.env.ref('delivery.free_delivery_carrier')

    carrier_id = fields.Many2one(default=_get_default_carrier)

    weight = fields.Float(compute='_compute_weight', string='Peso total', readonly=True, store=True)
    weight_uom_name = fields.Char(string='Unidad de peso', compute='_compute_weight_uom_name')

    @api.depends('partner_shipping_id')
    def _compute_available_carrier(self):
        res = super(SaleOrder,self)._compute_available_carrier()
        self.carrier_id = self.env.ref('delivery.free_delivery_carrier')
        return res

    @api.depends('order_line.product_uom_qty')
    def _compute_weight(self):
        for order in self:
            weight = qty = 0.0
            # filtro los que no son productos (secciones / notas)
            for line in order.order_line.filtered(lambda x: not x.display_type):
                qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
                weight += (line.product_id.weight or 0.0) * qty
            order.update({
                'weight': weight,
            })

    # @api.depends()
    def _compute_weight_uom_name(self):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        for order in self:
            order.weight_uom_name = weight_uom_id.name

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

    @api.multi
    def write(self, values):
        if self.user_has_groups('pronto.group_commitment_date_required'):
            if 'state' in values:
                if values['state'] == 'sale':
                    if not self.commitment_date:
                        raise UserError(
                                'Debe informar la fecha de compromiso'
                                )
        return super(SaleOrder, self).write(values)

    @api.multi
    def update_prices(self):
        # for compatibility with product_pack module
        self.ensure_one()
        pack_installed = 'pack_parent_line_id' in self.order_line._fields
        for line in self.order_line.with_context(
                update_prices=True, pricelist=self.pricelist_id.id).filtered(lambda l: l.product_id.lst_price):
            # ponemos descuento en cero por las dudas en dos casos:
            # 1) si estamos cambiando de lista que discrimina descuento
            #  a lista que los incluye
            # 2) o estamos actualizando precios
            # (no sabemos de que lista venimos) a una lista que no discrimina
            #  descuentos y existen listas que discriminan los
            if hasattr(self, '_origin') and self._origin.pricelist_id.\
                discount_policy == 'with_discount' and self.\
                pricelist_id.discount_policy != 'with_discount' or self.\
                    pricelist_id.discount_policy == 'with_discount'\
                    and self.env['product.pricelist'].search(
                        [('discount_policy', '!=', 'with_discount')], limit=1):
                line.discount = False
            # if pack_installed:
            #     if line.pack_parent_line_id:
            #         continue
            #     elif line.pack_child_line_ids:
            #         line.expand_pack_line()
            line.product_uom_change()
            line._onchange_discount()
        return True