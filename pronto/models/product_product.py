from odoo import models
from odoo.osv import expression

class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_domain_locations_new(self, location_ids, company_id=False, compute_child=True):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = super(
            ProductProduct, self)._get_domain_locations_new(
            location_ids=location_ids,
            company_id=company_id,
            compute_child=compute_child)
        excluded_location_ids = self.env['stock.location'].search([]).filtered(lambda x: x.computar_stock_disponible==False).mapped('id')
        if excluded_location_ids:
            domain_quant_loc = expression.AND([
                [("location_id", "not in", excluded_location_ids)],
                domain_quant_loc,
            ])
            domain_move_in_loc = expression.AND([
                [("location_dest_id", "not in", excluded_location_ids)],
                domain_move_in_loc,
            ])
            domain_move_out_loc = expression.AND([
                [("location_id", "not in", excluded_location_ids)],
                domain_move_out_loc,
            ])
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc