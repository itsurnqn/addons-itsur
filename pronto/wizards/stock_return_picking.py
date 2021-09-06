##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    reason_id = fields.Many2one(comodel_name="stock.return.picking.reason", string= 'Motivo de devolución')
    wait_replacement = fields.Boolean('Wait for vendor replacement', default=True)
    in_out = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'), ('internal', 'Internal')], related='picking_id.picking_type_id.code')

    @api.model
    def default_get(self, field_names):
        defaults = super(
            StockReturnPicking, self).default_get(field_names)
        picking_id = self.env['stock.picking'].browse(self.env.context['active_id'])
        defaults['in_out'] = picking_id.picking_type_id.code
        return defaults

    @api.multi
    def _create_returns(self):
        # add to new picking for return the reason for the return
        new_picking, pick_type_id = super()._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'reason_id': self.reason_id.id})
    
        if self.in_out == 'incoming' and self.wait_replacement:
            picking_type_id = self.picking_id.picking_type_id.id
            new_picking2 = self.picking_id.copy({
                'move_lines': [],
                'picking_type_id': picking_type_id,
                'state': 'draft',
                'origin': self.picking_id.origin,
                'location_id': self.location_id.id,
                'location_dest_id': self.picking_id.location_dest_id.id})

            # new_picking2.message_post_with_view('mail.message_origin_link',
            #     values={'self': new_picking2, 'origin': self.picking_id},
            #     subtype_id=self.env.ref('mail.mt_note').id)

            returned_lines = 0
            for return_line in self.product_return_moves:
                if not return_line.move_id:
                    raise UserError(_("You have manually created product lines, please delete them to proceed."))
                # TODO sle: float_is_zero?
                if return_line.quantity:
                    returned_lines += 1
                    vals = self._prepare_move_default_values(return_line, new_picking2)
                    vals['location_id'] = self.location_id.id or return_line.move_id.location_id.id
                    vals['location_dest_id'] = return_line.move_id.location_dest_id.id

                    res = return_line.move_id.copy(vals)
                    vals = {}
                    # import pdb; pdb.set_trace()
                    move_orig_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                    move_dest_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                    vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line.move_id]
                    vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                    res.write(vals)
            if not returned_lines:
                raise UserError(_("Please specify at least one non-zero quantity."))

            new_picking2.action_confirm()
            new_picking2.action_assign()

        return new_picking, pick_type_id
