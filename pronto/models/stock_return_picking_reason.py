##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api

class StockReturnPickingReason(models.Model):
	_name = 'stock.return.picking.reason'
	_description = 'Motivo de devolución'

	name = fields.Char('Descripción')