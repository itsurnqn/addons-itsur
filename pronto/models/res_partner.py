##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TipoCliente(models.Model):
	_name = 'sale.tipo.cliente'
	_description = 'Tipo de cliente'

	name = fields.Char('Nombre')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tipo_cliente_id = fields.Many2one('sale.tipo.cliente',string='Tipo Cliente', ondelete='Restrict')
