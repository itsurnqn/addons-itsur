##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.constrains('product_tmpl_id','pricelist_id','categ_id')
    def _verificar_duplicados(self):
        if not self.id:
            return

        descripcion = ""
        if self.applied_on == '1_product':
            item = self.env['product.pricelist.item'].search([('product_tmpl_id','=',self.product_tmpl_id.id),
                                                            ('pricelist_id','=',self.pricelist_id.id),
                                                            ('id','!=',self.id)])
            descripcion = "producto"
            
        elif self.applied_on == '2_product_category':
            item = self.env['product.pricelist.item'].search([('categ_id','=',self.categ_id.id),
                                                            ('pricelist_id','=',self.pricelist_id.id),
                                                            ('id','!=',self.id)])
            descripcion = "categoría"            
        else:
            item = False

        if item:
            raise ValidationError("Este {} ya tiene precio asignado en esta lista ".format(descripcion))
            # self.env.user.notify_danger(message="Este %s ya tiene precio asignado en esta lista " % descripcion)        

    @api.multi
    def write(self, values):
        res = super(ProductPricelistItem,self).write(values)
        if self.pricelist_id == self.env.user.company_id.product_pricelist_cost_id and self.product_tmpl_id:
            self.product_tmpl_id._actualizar_costo(self.product_tmpl_id.id)

        return res
       
    @api.model
    def create(self,values):
        res = super(ProductPricelistItem,self).create(values)
        if res.pricelist_id == self.env.user.company_id.product_pricelist_cost_id and res.product_tmpl_id:
            res.product_tmpl_id._actualizar_costo(res.product_tmpl_id.id)            

        return res    