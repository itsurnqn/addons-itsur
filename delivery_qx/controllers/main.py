##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route
from odoo.tools import config

class WebsiteSaleDelivery(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        res = super()._get_mandatory_billing_fields()
        # import pdb; pdb.set_trace()
        if 'city' in res:
            res.remove("city")
        if 'country_id' in res:
            res.remove("country_id")

        return res

    def _get_mandatory_shipping_fields(self):
        res = super()._get_mandatory_shipping_fields()
        # import pdb; pdb.set_trace()
        if 'city' in res:
            res.remove("city")
        if 'country_id' in res:
            res.remove("country_id")

        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super().checkout_form_validate(
            mode=mode, all_form_values=all_form_values, data=data)

        zip = all_form_values['zip']

        zip_id = request.env['res.city.zip'].sudo().search([('name','=',zip)])

        if not zip_id:
            error["zip"] = 'error'
            error_message.append('Código postal inválido')

        return error, error_message
    
    def _checkout_form_save(self, mode, checkout, all_values):
        res = super()._checkout_form_save(
            mode=mode, checkout=checkout, all_values=all_values)

        zip = all_values.get('zip', False)

        zip_id = request.env['res.city.zip'].sudo().search([('name','=',zip)])

        partner = res
        partner_id = request.env['res.partner'].sudo().browse(partner)

        values = {
            'zip_id': zip_id.id,
            'city_id': zip_id.city_id.id,
            'city': zip_id.city_id.name,
            'state_id': zip_id.city_id.state_id.id,
            'country_id': zip_id.city_id.country_id.id,
        }

        partner_id.sudo().write(values)

        return res
