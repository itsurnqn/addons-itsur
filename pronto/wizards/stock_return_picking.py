##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    reason_id = fields.Many2one(comodel_name="stock.return.picking.reason", string= 'Motivo de devolución')

    @api.multi
    def _create_returns(self):
        # add to new picking for return the reason for the return
        new_picking, pick_type_id = super()._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'reason_id': self.reason_id.id})
        return new_picking, pick_type_id
