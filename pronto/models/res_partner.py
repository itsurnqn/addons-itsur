##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class TipoCliente(models.Model):
	_name = 'sale.tipo.cliente'
	_description = 'Tipo de cliente'

	name = fields.Char('Nombre')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tipo_cliente_id = fields.Many2one('sale.tipo.cliente',string='Tipo Cliente', ondelete='Restrict')

    property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Pricelist', compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist", company_dependent=False, store=True,
        help="This pricelist will be used, instead of the default one, for sales to the current partner")

    @api.multi
    def write(self, values):
        super(ResPartner,self).write(values)
        if 'sale_type' in values:
            if not self.user_has_groups('pronto.group_ventas_cambiar_tipo_venta_contacto'):
                create_from_website = self._context.get('create_from_website', False)
                if not create_from_website:
                    raise ValidationError("Su usuario no posee permisos para modificar el tipo de venta")
   
