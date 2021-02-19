##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route
from odoo.tools import config

class ProntoWebsiteSale(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        """Inherit method in order to do not break Odoo tests"""
        res = super()._get_mandatory_billing_fields()
        if not config['test_enable']:
            res += ["zip"]
        
        # tabular ciudades
        if 'city' in res:
            res.remove("city")
        if 'country_id' in res:
            res.remove("country_id")

        return res + [
            "main_id_category_id", "main_id_number",
            "afip_responsability_type_id",
        ]

    def _get_mandatory_shipping_fields(self):
        res = super()._get_mandatory_shipping_fields()

        # tabular ciudades
        if 'city' in res:
            res.remove("city")
        if 'country_id' in res:
            res.remove("country_id")

        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super().checkout_form_validate(
            mode=mode, all_form_values=all_form_values, data=data)
        write_error, write_message = \
            request.env['res.partner'].sudo().try_write_commercial(
                all_form_values)
        if write_error:
            error.update(write_error)
            error_message.extend(write_message)

        # tabular ciudades
        zip = all_form_values['zip']
        zip_id = request.env['res.city.zip'].sudo().search([('name','=',zip)])
        if not zip_id:
            error["zip"] = 'error'
            error_message.append('Código postal inválido')

        return error, error_message

    def _checkout_form_save(self, mode, checkout, all_values):
        if all_values.get('commercial_partner_id', False):
            commercial_fields = [
                'main_id_number', 'main_id_category_id',
                'afip_responsability_type_id']
            for item in commercial_fields:                
                value = all_values.pop(item, False)
                if value:
                    checkout[item] = value
        res = super()._checkout_form_save(
            mode=mode, checkout=checkout, all_values=all_values)

        zip = all_values.get('zip', False)

        zip_id = request.env['res.city.zip'].sudo().search([('name','=',zip)])

        partner_id = request.env['res.partner'].sudo().browse(res)

        # tipo_cliente_id = request.env.ref('_pronto.usuario_final')
        # sale_type = request.env.ref('_pronto.contado')
        public_partner_id = request.env.ref('base.public_partner')

        values = {
            # 'tipo_cliente_id': tipo_cliente_id.id,
            'tipo_cliente_id': public_partner_id.tipo_cliente_id.id,
            # 'sale_type': sale_type.id,
            'sale_type': public_partner_id.sale_type.id,
            'property_product_pricelist': public_partner_id.property_product_pricelist.id,
            'zip_id': zip_id.id,
            'city_id': zip_id.city_id.id,
            'city': zip_id.city_id.name,
            'state_id': zip_id.city_id.state_id.id,
            'country_id': zip_id.city_id.country_id.id,
        }

        partner_id.sudo().write(values)

        order = request.website.sale_get_order()
        order.commitment_date = order.expected_date
        
        return res

    @route()
    def address(self, **kw):
        response = super().address(**kw)
        document_categories = request.env[
            'res.partner.id_category'].sudo().search([])
        afip_responsabilities = request.env[
            'afip.responsability.type'].sudo().search([])

        order = request.website.sale_get_order()
        partner_id = int(kw.get('partner_id', -1))

        Partner = request.env['res.partner']
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            uid = request.session.uid or request.env.ref('base.public_user').id
            Partner = request.env['res.users'].browse(uid).partner_id
            Partner = Partner.with_context(show_address=1).sudo()           
        else:
            if partner_id > 0:
                Partner = request.env['res.partner'].browse(partner_id)
                Partner = Partner.with_context(show_address=1).sudo()

        response.qcontext.update({
            'document_categories': document_categories,
            'afip_responsabilities': afip_responsabilities,
            'partner': Partner,
        })
        return response

    # NOTE this a copy of original odoo code that was added and edited here
    # because it was not able to inherit in other way.
    @route()
    def checkout(self, **post):
        super().checkout(**post)

        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        # ODOO ORIGINAL CODE
        """
        for f in self._get_mandatory_billing_fields():
            if not order.partner_id[f]:
                return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)
        """
        # OUR CODE START
        mandatory_billing_fields = self._get_mandatory_billing_fields()
        commercial_billing_fields = ["main_id_category_id", "main_id_number",
                                     "afip_responsability_type_id"]
        for item in commercial_billing_fields:
            mandatory_billing_fields.pop(mandatory_billing_fields.index(item))

        for f in mandatory_billing_fields:
            if not order.partner_id[f]:
                return request.redirect(
                    '/shop/address?partner_id=%d' % order.partner_id.id)
        for f in commercial_billing_fields:
            if not order.partner_id.commercial_partner_id[f]:
                return request.redirect(
                    '/shop/address?partner_id=%d' % order.partner_id.id)
        # OUR CODE END

        values = self.checkout_values(**post)

        if post.get('express'):
            return request.redirect('/shop/confirm_order')

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)