from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('main_id_number')
    def _check_main_id_number_unique(self):
        for record in self:
            # if record.parent_id or not record.vat:
            #     continue
            # test_condition = (config['test_enable'] and
            #                   not self.env.context.get('test_vat'))
            # if test_condition:
            #     continue
            results = self.env['res.partner'].search_count([
                ('parent_id', '=', False),
                ('main_id_number', '=', record.main_id_number),
                ('id', '!=', record.id)
            ])
            if results:
                raise ValidationError(_(
                    "El número de identificación %s ya existe en otro "
                    "contacto.") % record.main_id_number)
