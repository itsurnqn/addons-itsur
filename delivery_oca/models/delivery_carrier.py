##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('oca', "OCA")])

    def oca_rate_shipment(self, order):
            
        try:
            price_unit = self._get_price_available_oca(order)

            # import pdb; pdb.set_trace()

            # agregar seguro
            valor_declarado = order.amount_untaxed
            
            # .1 si el presu esta en dolares, tengo que pasar
            # valor_declarado a pesos
            if order.currency_id != order.company_id.currency_id:
                valor_declarado = order.currency_id._convert(
                            valor_declarado, order.company_id.currency_id, order.company_id, order.date_order or fields.Date.today())                

            costo_seguro = 0
            if valor_declarado * self.porcentaje_seguro/100 > self.costo_minimo_seguro:
                costo_seguro = valor_declarado * self.porcentaje_seguro/100
            else:
                costo_seguro = self.costo_minimo_seguro
            
            # print(price_unit, costo_seguro)
            price_unit = price_unit + costo_seguro + self.costo_embalaje_picking

            # .2 si el presu esta en dolares, tengo que pasar price_unit a dolares
            if order.currency_id != order.company_id.currency_id:
                price_unit = order.company_id.currency_id._convert(
                            price_unit, order.currency_id, order.company_id, order.date_order or fields.Date.today())
                            
        except UserError as e:
            return {'success': False,
                    'price': 0.0,
                    'error_message': e.name,
                    'warning_message': False}

        return {'success': True,
                'price': price_unit,
                'error_message': False,
                'warning_message': False}

    def _get_price_available_oca(self, order):
        self.ensure_one()
        total = weight = volume = quantity = 0
        total_delivery = 0.0
        for line in order.order_line.filtered(lambda x: not x.product_id.pack_ok):
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty
            quantity += qty
        total = (order.amount_total or 0.0) - total_delivery

        # total = order.currency_id._convert(
        #     total, order.company_id.currency_id, order.company_id, order.date_order or fields.Date.today())

        # import pdb; pdb.set_trace()
        
        zona_oca_id = order.partner_shipping_id.zip_id.zona_oca_id
        # import pdb; pdb.set_trace()
        # print(total, weight, volume, quantity, zona_qx_id)
        return self._get_price_from_picking_oca(total, weight, volume, quantity, zona_oca_id)

    def _get_price_from_picking_oca(self, total, weight, volume, quantity, zona_oca_id):
        price = 0.0
        criteria_found = False
        price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume * weight, 'quantity': quantity, 'zone': zona_oca_id.id}
        for line in self.price_rule_ids:
            test = safe_eval(line.variable + line.operator + str(line.max_value) + ' and zone=={}'.format(line.zona_oca_id.id), price_dict)
            if test:
                # import pdb; pdb.set_trace()
                price = line.list_base_price + line.list_price * price_dict[line.variable_factor]
                criteria_found = True
                break
        if not criteria_found:
            raise UserError(_("No price rule matching this order; delivery cost cannot be computed."))

        return price