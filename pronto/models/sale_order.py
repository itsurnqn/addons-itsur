# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    costo_total_pesos = fields.Float(string = 'Costo total pesos', compute='_computed_costo_total_pesos', readonly=False, store=True)
    precio_total_pesos = fields.Float(string = 'Precio total pesos', compute='_computed_precio_total_pesos', readonly=False, store=True, copy=False)

    excluir_markup = fields.Boolean(string="Excluir del calculo del mark-up (Porcentaje) en los pedidos",
                    compute='_computed_excluir_markup', 
                    readonly=False, 
                    store=True)
    
    @api.depends('product_id','product_id.excluir_calculo_markup')
    def _computed_excluir_markup(self):
        for rec in self:
            if rec.product_id.excluir_calculo_markup == 'siempre':                
                rec.excluir_markup = True
            elif rec.product_id.excluir_calculo_markup == 'componente_pack':
                if rec.pack_parent_line_id:
                    rec.excluir_markup = True
            else:
                rec.excluir_markup = False

    @api.depends('product_id', 'product_uom_qty','purchase_price')
    def _computed_costo_total_pesos(self):
        # import pdb; pdb.set_trace()

        for rec in self:        
            if rec.display_type:
                # es una sección
                continue

            costo_total_pesos = rec.product_uom_qty * rec.purchase_price
            if rec.order_id.pricelist_id.currency_id != rec.env.user.company_id.currency_id:
                rec.costo_total_pesos = costo_total_pesos * rec.order_id.cotizacion
            else:
                rec.costo_total_pesos = costo_total_pesos

    @api.depends('product_id', 'product_uom_qty','purchase_price', 'price_unit', 'order_id.pricelist_id', 'discount')    
    def _computed_precio_total_pesos(self,precio_total=False):
        # se llama desde lo módulo clima
        # clima es el que determina el precio_total (sin desc. clima)
        
        for rec in self:
            if rec.display_type:
                # es una sección
                continue
            
            if precio_total:
                precio_total_pesos = precio_total
            else:
                precio_total_pesos = rec.price_subtotal
                
            # precio_total_pesos = rec.product_uom_qty * rec.price_unit
            if rec.order_id.pricelist_id.currency_id != rec.env.user.company_id.currency_id:
                rec.precio_total_pesos = precio_total_pesos * rec.order_id.cotizacion
            else:
                rec.precio_total_pesos = precio_total_pesos
    
            if rec.product_id.pack_ok and rec.product_id.pack_type == 'detailed' and rec.product_id.pack_component_price == 'detailed':
                # el precio_total_pesos está en los componentes del pack
                rec.precio_total_pesos = 0
            
        # import pdb; pdb.set_trace()

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

    # el update_price de adhoc (sale_ux) dispara este método
    # y llamando a product_id_change_margin se recalcula y convierte la moneda del costo
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(SaleOrderLine, self).product_uom_change()
        self.product_id_change_margin()
        # si es un componente de un pack de tipo DT, que lo ponga en 0.
        if self.pack_parent_line_id:
            if self.pack_parent_line_id.product_id.pack_component_price == 'totalized':
                self.price_unit = 0
        return res

    @api.multi
    def button_cancel_remaining(self):
        if self.pack_child_line_ids:
            # es un pack
            if self.product_id.pack_type == 'detailed':
                if self.product_id.pack_component_price in ['detailed','totalized']:

                    self.with_context(bypass_protecion=True).product_uom_qty = 0

                    for rec in self.pack_child_line_ids:
                        if rec.qty_delivered != 0:
                            raise UserError(_(
                                "La cancelación de lo pendiente en packs "
                                "SOLO puede ser invocada cuando no se entregó ningún componente del PACK."))
                        rec.with_context(
                            bypass_protecion=True).product_uom_qty = 0
                        to_cancel_moves = rec.move_ids.filtered(
                            lambda x: x.state not in ['done', 'cancel'])
                        to_cancel_moves._cancel_quantity()

                    self.order_id.message_post(
                        body=_(
                            'Llamada a cancelar pendientes para la línea "%s" (id %s)') % (
                                self.name, self.id))

                else:
                    raise UserError(_(
                        "La cancelación de lo pendiente "
                        "no puede ser invocada para este tipo de pack."))
            elif self.product_id.pack_type == 'non_detailed':
                raise UserError(_(
                    "La cancelación de lo pendiente "
                    "no puede ser invocada para este tipo de pack."))
            # elif self.pack_parent_line_id:
            #     raise UserError(_(
            #         "La cancelación de lo pendiente "
            #         "no puede ser invocada producto componente de un pack."))
        else:
            return super(SaleOrderLine, self).button_cancel_remaining()

    # src/addons/sale/models/sale.py:942
    # que contemple ...
    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status(self):
        super()._compute_invoice_status()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale', 'done'):
                line.invoice_status = 'no'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and\
                    float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
                line.invoice_status = 'upselling'
            elif float_compare(line.qty_invoiced + line.qty_returned, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                # import pdb; pdb.set_trace()
                line.invoice_status = 'no'

    # src/addons/sale_margin/models/sale_order.py:14
    # lo tengo que sobre-escribir porque no encuentro otra forma de hacerlo
    # Cuando es un pack detallado-totalizado, el costo del producto se debe totalizar en el pack
    # de la forma que estaba hecho (en expand_pack_line) fallaba en el update_price (botón de adhoc)
    def _compute_margin(self, order_id, product_id, product_uom_id):
        frm_cur = self.env.user.company_id.currency_id
        to_cur = order_id.pricelist_id.currency_id
        if product_id.pack_ok and product_id.pack_type == 'detailed' and product_id.pack_component_price == 'totalized':
            purchase_price = sum(product_id.pack_line_ids.mapped('product_id.standard_price'))
        else:
            purchase_price = product_id.standard_price
        if product_uom_id != product_id.uom_id:
            purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
        price = frm_cur._convert(
            purchase_price, to_cur, order_id.company_id or self.env.user.company_id,
            order_id.date_order or fields.Date.today(), round=False)
        return price



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_default_carrier(self):
        return self.env.ref('delivery.free_delivery_carrier')

    carrier_id = fields.Many2one(default=_get_default_carrier)

    weight = fields.Float(compute='_compute_weight', string='Peso total', readonly=True, store=True)
    weight_uom_name = fields.Char(string='Unidad de peso', compute='_compute_weight_uom_name')

    cotizacion = fields.Float(string='Cotización',help='Cotización de la moneda del pedido respecto a la moneda de la companía.')

    debt_balance_currency_id = fields.Many2one(
        string='Company Currency',
        related='company_id.currency_id',
    )

    debt_balance = fields.Monetary(
        related='partner_id.debt_balance',
        currency_field = 'debt_balance_currency_id',
        string = 'Saldo'
    )

    sale_order_reference = fields.Char("Referencia")

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
        # import pdb; pdb.set_trace()
        for line in self.order_line.filtered(lambda x: x.product_id.type == 'service' and x.product_id.entregar_al_confirmar_prespuesto):
            line.qty_delivered = line.product_uom_qty

    @api.multi
    def write(self, values):
        if self.user_has_groups('pronto.group_commitment_date_required'):
            if ('state' in values and self.state != 'done' and values['state'] == 'sale') or 'user_requesting_review' in values:
                    if not self.commitment_date:
                        raise UserError(
                                'Debe informar la fecha de compromiso'
                                )

        if self.user_has_groups('pronto.group_ventas_solo_lectura_pedidos'):
            raise ValidationError("Su usuario solo está habilitado para escribir en el chatter ")        
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
        
        self._obtener_cotizacion()

        return True

    @api.multi
    def _obtener_cotizacion(self):
        if self.pricelist_id:
            # moneda_origen = self.pricelist_id.currency_id
            moneda_origen = self.env.ref('base.USD')
            moneda_destino = self.env.user.company_id.currency_id
            compania = self.env.user.company_id

            self.cotizacion = moneda_origen._convert(1,moneda_destino,compania, self.date_order)

    @api.depends('order_line.margin','order_line.product_id.excluir_calculo_markup')
    def _product_margin(self):
        for order in self:
            order.margin = sum(order.order_line.filtered(lambda r: r.state != 'cancel' and not r.excluir_markup).mapped('margin'))

    @api.onchange('pricelist_id')
    def _onchange_pricelist(self):
        super()._onchange_pricelist()
        for line in self.order_line.filtered(lambda x: x.product_id.pack_ok and x.product_id.pack_type == 'detailed' and x.product_id.pack_component_price == 'totalized'):
            line.purchase_price = sum(line.pack_child_line_ids.mapped('purchase_price'))

    @api.model
    def create(self,values):
        res = super(SaleOrder,self).create(values)
        # esto lo hago porque sino cuando duplico un pedido
        # no quedan bien el precio_total_pesos de cada renglón
        res.update_prices()
        return res