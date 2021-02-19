##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import dateutil.parser
import logging
_logger = logging.getLogger(__name__)

class ProductPricelistItem(models.Model):
    _name = 'product.pricelist.item'
    _inherit = ['product.pricelist.item', 'mail.thread', 'mail.activity.mixin']

    # @api.multi
    # def _default_fecha_ultima_modificacion_precio(self):
    #     # return dateutil.parser.parse(self.write_date).date()
    #     import pdb; pdb.set_trace()
    #     if self.write_date:
    #         fecha = self.write_date.date()
    #     else:
    #         fecha = fields.Date.context_today(self)

    #     return fecha

    fecha_ultima_modificacion_precio = fields.Date(string="Fecha última modificación precio")
                                                    # default=_default_fecha_ultima_modificacion_precio,
                                                    # required=True)

    fecha_ultimo_control = fields.Date(string="Fecha último control")
    usuario_ultimo_control = fields.Many2one(comodel_name="res.users", string="Usuario último control")

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
        if 'fixed_price' in values:
            if self.pricelist_id == self.env.user.company_id.product_pricelist_cost_id and self.product_tmpl_id:
                self.product_tmpl_id._actualizar_costo(self.product_tmpl_id.id)            
                self.set_fixed_price(self.id,self.product_tmpl_id.id,self.fixed_price)
                self.fecha_ultima_modificacion_precio = fields.Date.context_today(self)
        return res
       
    @api.model
    def create(self,values):
        res = super(ProductPricelistItem,self).create(values)
        if res.pricelist_id == self.env.user.company_id.product_pricelist_cost_id and res.product_tmpl_id:
            res.product_tmpl_id._actualizar_costo(res.product_tmpl_id.id)            
            self.set_fixed_price(res.id,res.product_tmpl_id.id,res.fixed_price)
            res.fecha_ultima_modificacion_precio = fields.Date.context_today(self)
        return res
    
    @api.multi
    def set_fixed_price(self,item_id,product_tmpl_id,fixed_price):
        item_history = self.env["product.pricelist.item.history"]
        item_history.create({
            'product_tmpl_id': product_tmpl_id,
            'fixed_price': fixed_price,
            'pricelist_item_id': item_id
        })

    @api.onchange('fecha_ultimo_control')
    def fecha_ultimo_control_change(self):
        if self.fecha_ultimo_control: 
            self.usuario_ultimo_control = self.env.user
        else:
            self.usuario_ultimo_control = False

    @api.model
    def setear_fecha_ultima_modificacion_precio(self):
        items = self.env["product.pricelist.item"].search([('pricelist_id','=',self.env.user.company_id.product_pricelist_cost_id.id)])

        c = 0
        total = len(items)
        # import pdb; pdb.set_trace()
        for i in items:
            if i.write_date:
                i.fecha_ultima_modificacion_precio = i.write_date.date()
                c += 1
                _logger.info("faltan: %s" % str(total - c))
                # i.write({'fecha_ultima_modificacion_precio': i.write_date.date()})