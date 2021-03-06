##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_default_uom_id(self):
        return 0

    uom_id = fields.Many2one(default=_get_default_uom_id)
    uom_po_id = fields.Many2one(default=_get_default_uom_id)

    categ_id = fields.Many2one(default=0)

    show_components_to_customer = fields.Boolean("Mostrar componentes al cliente", default=True)

    # si lo hago así, lo hace a nivel de db y todos los productos ya cargados deben tener informado el código
    # mejor por xml o en el write/create
    # default_code = fields.Char(required=True)
    
    entregar_al_confirmar_prespuesto = fields.Boolean(string="Entregar al confirmar el pedido",
                    default=True, 
                    help="Si está tildado, el servicio se pone como entregado al confirmar el presupuesto")

    dias_costo_sin_actualizar = fields.Integer(string="Días costo sin actualizar",
                                help= "Días tomados en cuenta hasta mostrar una actividad porque el costo no fue actualizado o no se realizó una verificación manual")

    @api.model
    def _actualizar_costo(self, product_tmpl_id = 0):

        pricelist = self.env.user.company_id.product_pricelist_cost_id
        res_company = self.env.user.company_id
        res_currency = self.env.user.company_id.currency_id
        cantidad = 1

        if product_tmpl_id:
            # SOLO por cambio en el precio en la lista de costo (no por cambio en la cotización de dolar)
            producto = self.env['product.template'].with_context(controlar_requeridos = False,actualizar_costo_producto_fabricado = True).browse(product_tmpl_id)
            # SOLO si no es fabricado (el costo del fabricado se calcula a partir del costo de los componentes)
            if not producto.bom_ids:
                product_price = pricelist.get_product_price(producto.product_variant_id,cantidad,self.env.user.partner_id)
                producto.standard_price = pricelist.currency_id._convert(product_price,res_currency,res_company,datetime.today())
        else:            
            param = self.env['ir.config_parameter'].sudo()
            tasa_actualizacion_costo = float(param.get_param('pronto.tasa_actualizacion_costo'))
            tasa_actual = res_currency.rate
            # HACER SOLO si cambia la cotización
            if tasa_actualizacion_costo != tasa_actual:
                _logger.info("Iniciando la actualizacion de costos.")
                param.set_param('pronto.tasa_actualizacion_costo',str(tasa_actual))
                # Nota: primero tengo que actualizar materias primas y después productos fabricados (se calculan a partir de los primeros)
                # materias primas
                materias_primas = self.env['product.template'].with_context(active_test=False).search([('bom_ids', '=', False)])
                # productos fabricados
                productos_fabricados = self.env['product.template'].with_context(active_test=False).search([('bom_ids', '!=', False)])

                # productos = self.env['product.template'].with_context(active_test=False).search([])
                for rec in materias_primas:

                    # with_context: que no controle campos requeridos
                    # with_context: al actualizar costo de materia prima, que no dispare la actualización de los que se fabrican con esa materia prima
                    # (los actualizo por separado para que no se duplique el histórico)
                    rec = rec.with_context(controlar_requeridos = False,actualizar_costo_producto_fabricado = False)

                    if rec.product_variant_id:
                        
                        
                        # monto = 1
                        
                        product_price = pricelist.get_product_price(rec.product_variant_id,cantidad,self.env.user.partner_id)
                        rec.standard_price = pricelist.currency_id._convert(product_price,res_currency,res_company,datetime.today())

                if productos_fabricados:
                    productos_fabricados.action_bom_cost()

                _logger.info("Se actualizo el costo de %d productos.", len(materias_primas) + len(productos_fabricados))

    @api.model
    def create(self,values):
        # import pdb; pdb.set_trace()
        # if 'type' in values or 'pack_ok' in values:
        if values['pack_ok'] and values['type'] !='service':
            raise UserError("El Tipo de producto de los pack´s debe ser 'Servicio' ")

        if not self.user_has_groups('pronto.group_no_exigir_campos_producto_vendible'):
            mensaje_validacion = ""
            if values['sale_ok'] and values['type'] == 'product':
                if values['weight'] == 0:
                    mensaje_validacion += "- peso \n"
                if values['volume'] == 0:
                    mensaje_validacion += "- volumen \n"
                if not values['image_medium']:
                    mensaje_validacion += "- imagen del producto \n"
                if not values['barcode']:
                    mensaje_validacion += "- codigo de barras \n"

                item_lista_precio = self.item_ids.filtered(lambda x: x.pricelist_id.id == 2)
                if not item_lista_precio:
                    mensaje_validacion += "- precio en la tarifa Costo \n"

                proveedores = self.seller_ids
                if not proveedores:
                    mensaje_validacion += "- Proveedor \n"

            if mensaje_validacion:
                raise ValidationError("Debe completar los siguientes campos para que el producto pueda ser vendido: \n\n" + mensaje_validacion)

        res = super(ProductTemplate,self).create(values)

        return res

    @api.multi
    def write(self, values):
        super(ProductTemplate,self).write(values)        
        if 'type' in values or 'pack_ok' in values:
            if self.pack_ok and self.type !='service':
                raise UserError("El Tipo de producto de los pack´s debe ser 'Servicio'")
        
        controlar_requeridos = self.env.context.get('controlar_requeridos', True)

        if controlar_requeridos:
            if not self.user_has_groups('pronto.group_no_exigir_campos_producto_vendible'):
                for rec in self:
                    mensaje_validacion = ""
                    if rec.type == 'product' and rec.sale_ok and rec.weight == 0:
                        mensaje_validacion += "- peso \n"

                    if rec.type == 'product' and rec.sale_ok and rec.volume == 0:
                        mensaje_validacion += "- volumen \n"

                    if rec.type == 'product' and rec.sale_ok and not rec.image_medium:
                        mensaje_validacion += "- imagen del producto \n"

                    if rec.type == 'product' and rec.sale_ok and not rec.barcode:
                        mensaje_validacion += "- codigo de barras \n"

                    if rec.type == 'product' and rec.sale_ok:
                        item_lista_precio = rec.item_ids.filtered(lambda x: x.pricelist_id.id == 2)
                        if not item_lista_precio:
                            mensaje_validacion += "- el precio en la tarifa Costo \n"
                        else:
                            if item_lista_precio.compute_price == 'fixed' and item_lista_precio.fixed_price == 0:
                                mensaje_validacion += "- el precio (distinto de 0) en la tarifa Costo \n"

                    if rec.type == 'product' and rec.sale_ok:
                        proveedores = rec.seller_ids
                        if not proveedores:
                            mensaje_validacion += "- Proveedor \n"
                        else:
                            proveedor = proveedores[0]
                            if proveedor.price == 0:
                                mensaje_validacion += "- el precio en el proveedor \n"

                    if mensaje_validacion:
                        detalle_mensaje = mensaje_validacion
                        mensaje_validacion = ""
                        raise ValidationError("Ref. Interna: {} \n\n Debe completar los siguientes campos para que el producto pueda ser vendido: \n\n {}".format(
                                                    rec.default_code,
                                                    detalle_mensaje
                                            ))

        actualizar_costo_producto_fabricado = self.env.context.get('actualizar_costo_producto_fabricado', True)
        # standard_price solo se actualiza desde el backend (por código: al cambiar el precio en la lista de costo o por tarea programada)
        # actualizar_costo_producto_fabricado = False, para que no se actualice desde la tarea programada.
        if 'standard_price' in values and actualizar_costo_producto_fabricado:
            bom_line_ids = self.env['mrp.bom.line'].search([('product_id','=',self.product_variant_id.id)])
            # es materia prima de un producto fabricado?
            if bom_line_ids:
                for line in bom_line_ids:
                    # recalculo el costo del producto fabricado
                    line.bom_id.product_tmpl_id.action_bom_cost()

        return