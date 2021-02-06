##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_quote_log_ids = fields.One2many('sale.order.quote.log','sale_order_id',String="Logs del pedido", copy=False)
    # actualizo_precios = fields.Boolean('Actualizo precios', Default=False)

    @api.multi
    def write(self, values):     
        super(SaleOrder,self).write(values)
        
        if self.state in ('draft','sent'):
            delta = self.validity_date - fields.Date.context_today(self)

            # self.env['sale.order.quote.log'].search([('log_type','=','validez')]).unlink()

            self.sale_order_quote_log_ids.filtered(lambda x: x.log_type == 'validez').unlink()
            if delta.days < 0:
                self.registrar_log("Fecha de validez vencida: {}".format(self.validity_date),'validez')
            
            self.sale_order_quote_log_ids.filtered(lambda x: x.log_type == 'tipo_venta').unlink()
            if self.type_id != self.partner_id.sale_type:
                self.registrar_log("Tipo de venta no coincide con ficha cliente: {}".format(self.partner_id.sale_type.name),'tipo_venta')

            for line in self.order_line.filtered(lambda x: not x.display_type):
                if line.product_id.registrar_novedad_presupuesto:
                    # novedad: descuento en componente de pack
                    # import pdb; pdb.set_trace()
                    if line.pack_parent_line_id:
                        # es un componente de un pack
                        descuento_predefinido = line.pack_parent_line_id.product_id.pack_line_ids.filtered(lambda x: x.product_id.id == line.product_id.id).sale_discount 
                        descuento_modificado = line.discount
                        # import pdb; pdb.set_trace()

                        # log_anterior = self.env['sale.order.quote.log'].search(
                        #     [('product_id','=',line.product_id.id),
                        #     ('order_line_id','=',line.id),
                        #     ('log_type','=','descuento_componente_pack')])
                        
                        self.sale_order_quote_log_ids.filtered(lambda x: x.product_id == line.product_id 
                                                                and x.order_line_id == line 
                                                                and x.log_type == 'descuento_componente_pack').unlink()

                        # if log_anterior:
                        #     log_anterior.unlink()

                        if descuento_modificado > descuento_predefinido:                
                            self.registrar_log(
                                "Descuento predefinido: {} - Descuento modificado: {}".format(
                                    descuento_predefinido,
                                    descuento_modificado),'descuento_componente_pack', line, line.product_id)

                    if line.pack_parent_line_id and line.pack_parent_line_id.pack_type == 'detailed' and line.pack_parent_line_id.pack_component_price == 'totalized':
                        # el precio de los componentes están siempre en cero. No se controla la novedad de precios.
                        continue

                    # copiado desde: product_uom_change (addons/sale)
                    if line.order_id.pricelist_id and line.order_id.partner_id:                        
                        product = line.product_id.with_context(
                            lang=line.order_id.partner_id.lang,
                            partner=line.order_id.partner_id,
                            quantity=line.product_uom_qty,
                            # date=line.order_id.date_order,
                            date=fields.Datetime.now(),
                            pricelist=line.order_id.pricelist_id.id,
                            uom=line.product_uom.id,
                            fiscal_position=line.env.context.get('fiscal_position')
                        )
                        precio_unitario_actual = round(self.env['account.tax']._fix_tax_included_price_company(line._get_display_price(product), product.taxes_id, line.tax_id, line.company_id),2)

                        precio_unitario = round(line.price_unit,2)

                        self.sale_order_quote_log_ids.filtered(lambda x: x.product_id == line.product_id 
                                                                and x.order_line_id == line 
                                                                and x.log_type == 'precio').unlink()

                        # log_anterior = self.env['sale.order.quote.log'].search(
                        #     [('product_id','=',product.id),
                        #     ('order_line_id','=',line.id),
                        #     ('log_type','=','precio')])
                        
                        # if log_anterior:
                        #     log_anterior.unlink()

                        if precio_unitario != precio_unitario_actual:                
                            self.registrar_log(
                                "Precio anterior: {} - Precio nuevo: {}".format(
                                    precio_unitario,
                                    precio_unitario_actual),'precio', line, product)
                    

                    
        return 

    def registrar_log(self, description, log_type, order_line_id = None, product_id = None):
        
        vals = {
            'sale_order_id': self.id,
            'fecha_hora': fields.Datetime.now(),
            'description': description,
            'log_type': log_type
        }

        if product_id:
            vals['product_id'] = product_id.id

        if order_line_id:
            vals['order_line_id'] = order_line_id.id            
        
        log = self.env['sale.order.quote.log'].create(vals)

    @api.multi
    def update_prices(self):
        
        self.env['sale.order.quote.log'].search([('log_type','=','precio')]).unlink()
        
        return super(SaleOrder,self).update_prices()

class SaleOrderQuoteLog(models.Model):
    _name = 'sale.order.quote.log'
    _description = 'Logs de presupuestos'

    sale_order_id = fields.Many2one('sale.order',String="Pedido")
    order_line_id = fields.Many2one('sale.order.line',String="Línea de Pedido")
    fecha_hora = fields.Datetime(String="Fecha Log")
    description = fields.Char(string="Descripción")
    product_id = fields.Many2one('product.product')
    log_type = fields.Selection(
                            [('validez','Fecha Validez'),
                            ('precio','Precio'),
                            ('descuento_componente_pack','Descuento en componente de pack'),
                            ('tipo_venta','Tipo venta no coincide'),
                            ('otro','Otro')
                            ],'Tipo')
