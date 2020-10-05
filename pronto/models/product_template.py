##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_default_uom_id(self):
        return 0

    uom_id = fields.Many2one(default=_get_default_uom_id)
    uom_po_id = fields.Many2one(default=_get_default_uom_id)

    @api.model
    def _actualizar_costo(self):

        pricelist = self.env.user.company_id.product_pricelist_cost_id

        res_currency = self.env['res.currency'].browse(19)
        res_company = self.env.user.company_id
        fecha = datetime.today()
        monto = 1

        productos = self.env['product.template'].search([])
        # productos = self.env['product.template'].browse(1865)
        for rec in productos:
            cantidad = 1
            # self.env['product.pricelist'].browse(pricelist_id).get_product_price(self.product_variant_id,cantidad,partner)
            if rec.product_variant_id:
                product_price = pricelist.get_product_price(rec.product_variant_id,cantidad,self.env.user.partner_id)
                rec.standard_price = pricelist.currency_id._convert(product_price,res_currency,res_company,datetime.today())

    @api.model
    def create(self,values):
        if self.pack_ok and self.type !='service':
            raise UserError("El Tipo de producto de los pack´s debe ser 'Servicio' ")
        return super(ProductTemplate,self).create(values)

    @api.multi
    def write(self, values):
        super(ProductTemplate,self).write(values)        
        if 'type' in values or 'pack_ok' in values:
            if self.pack_ok and self.type !='service':
                raise UserError("El Tipo de producto de los pack´s debe ser 'Servicio'")
        return