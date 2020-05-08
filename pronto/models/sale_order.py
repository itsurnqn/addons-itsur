# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def invoice_line_create_vals(self, invoice_id, qty):
        self.mapped(
            'move_ids'
        ).filtered(
            lambda x: not x.invoice_line_id and
            not x.location_dest_id.scrap_location and
            x.location_dest_id.usage == 'customer'
        ).mapped(
            'picking_id'
        ).write({'invoice_ids': [(4, invoice_id)]})
        return super(SaleOrderLine, self).invoice_line_create_vals(invoice_id,
                                                                   qty)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        # import pdb; pdb.set_trace()
        if self.env.user.sale_journal_id:
            res['journal_id'] = self.env.user.sale_journal_id.id
        return res
