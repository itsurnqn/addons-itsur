##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.constrains('product_tmpl_id','pricelist_id')
    def _verificar_duplicados(self):
        if not self.id:
            return

        item = self.env['product.pricelist.item'].search([('product_tmpl_id','=',self.product_tmpl_id.id),
                                                        ('pricelist_id','=',self.pricelist_id.id),
                                                        ('id','!=',self.id)])
        if item:
            descripcion = ""
            
            if self.applied_on == '1_product':
                descripcion = "producto"
            elif self.applied_on == '2_product_category':                
                descripcion = "categoría"
            else:
                descripcion = "elemento"

            self.env.user.notify_danger(message="Este %s ya tiene precio asignado en esta lista " % descripcion)        