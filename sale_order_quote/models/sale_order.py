##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_quote_log_ids = fields.One2many('sale.order.quote.log','sale_order_id',String="Logs del pedido")
    # actualizo_precios = fields.Boolean('Actualizo precios', Default=False)

    @api.multi
    def write(self, values):     
        super(SaleOrder,self).write(values)
        
        delta = self.validity_date - fields.Date.context_today(self)

        self.env['sale.order.quote.log'].search([('log_type','=','validez')]).unlink()
        if delta.days < 0:
            self.registrar_log("Fecha de validez vencida: {}".format(self.validity_date),'validez')
            
        lista_precio = self.pricelist_id

        cantidad = 1        
        for line in self.order_line:
            product = line.product_id
            precio_unitario = round(line.price_unit,2)
            precio_unitario_actual = round(lista_precio.get_product_price(product.product_variant_id,cantidad,self.env.user.partner_id),2)

            log_anterior = self.env['sale.order.quote.log'].search(
                [('product_id','=',product.id),
                ('log_type','=','precio')])
            
            if log_anterior:
                log_anterior.unlink()

            if precio_unitario != precio_unitario_actual:                
                self.registrar_log(
                    "Precio anterior: {} - Precio nuevo: {}".format(
                        precio_unitario,
                        precio_unitario_actual),'precio', product)

        return 

    def registrar_log(self, description, log_type, product_id = None):
        
        vals = {
            'sale_order_id': self.id,
            'fecha_hora': fields.Datetime.now(),
            'description': description,
            'log_type': log_type
        }

        if product_id:
            vals['product_id'] = product_id.id
        
        log = self.env['sale.order.quote.log'].create(vals)

    @api.multi
    def update_prices(self):
        
        self.env['sale.order.quote.log'].search([('log_type','=','precio')]).unlink()
        
        return super(SaleOrder,self).update_prices()

class SaleOrderQuoteLog(models.Model):
    _name = 'sale.order.quote.log'
    _description = 'Logs de presupuestos'

    sale_order_id = fields.Many2one('sale.order',String="Pedido")
    fecha_hora = fields.Datetime(String="Fecha Log")
    description = fields.Char(string="Descripción")
    product_id = fields.Many2one('product.product')
    log_type = fields.Selection(
                            [('validez','Fecha Validez'),
                            ('precio','Precio'),
                            ('otro','Otro')
                            ],'Tipo')
