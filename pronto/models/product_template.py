##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_default_uom_id(self):
        return 0

    uom_id = fields.Many2one(default=_get_default_uom_id)
    uom_po_id = fields.Many2one(default=_get_default_uom_id)

    categ_id = fields.Many2one(default=0)

    # si lo hago así, lo hace a nivel de db y todos los productos ya cargados deben tener informado el código
    # mejor por xml o en el write/create
    # default_code = fields.Char(required=True)
    
    @api.model
    def _actualizar_costo(self):

        pricelist = self.env.user.company_id.product_pricelist_cost_id

        res_currency = self.env['res.currency'].browse(19)
        res_company = self.env.user.company_id
        fecha = datetime.today()
        monto = 1

        productos = self.env['product.template'].with_context(active_test=False).search([])
        # productos = self.env['product.template'].browse(1865)
        for rec in productos:
            cantidad = 1
            # self.env['product.pricelist'].browse(pricelist_id).get_product_price(self.product_variant_id,cantidad,partner)
            rec = rec.with_context(controlar_requeridos = False)
            if rec.product_variant_id:
                product_price = pricelist.get_product_price(rec.product_variant_id,cantidad,self.env.user.partner_id)
                rec.standard_price = pricelist.currency_id._convert(product_price,res_currency,res_company,datetime.today())

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

        return