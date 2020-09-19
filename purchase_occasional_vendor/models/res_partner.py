##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    occasional_vendor = fields.Boolean("Proveedor ocasional")

    @api.model
    def create(self, values):
        if 'occasional_vendor' in values:
            values['active'] = 0
        # import pdb; pdb.set_trace()
        return super(ResPartner, self).create(values)