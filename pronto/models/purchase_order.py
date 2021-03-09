##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def actualizar_costos(self):
        net_price_installed = 'net_price' in self.env[
            'product.supplierinfo']._fields
        for rec in self.order_line.filtered('price_unit'):
            producto = self.env['product.product'].browse([rec.product_id.id])
            producto.update({'standard_price': rec.price_unit})
            
            # import pdb; pdb.set_trace()

            # producto = self.env['product.product'].search([('id','=',rec.product_id.id)])
            
            # for rec in producto:
            #     rec.update({'standard_price': 50})
            
            # producto.browse([rec.product_id]).update({'standard_price': 50})

            # seller = rec.product_id._select_seller(
            #     partner_id=rec.order_id.partner_id,
            #     # usamos minimo de cantidad 0 porque si no seria complicado
            #     # y generariamos registros para cada cantidad que se esta
            #     # comprando
            #     quantity=0.0,
            #     date=rec.order_id.date_order and
            #     rec.order_id.date_order.date(),
            #     # idem quantity, no lo necesitamos
            #     uom_id=False,
            # )
            # if not seller:
            #     seller = self.env['product.supplierinfo'].create({
            #         'date_start': rec.order_id.date_order and
            #         rec.order_id.date_order.date(),
            #         'name': rec.order_id.partner_id.id,
            #         'product_tmpl_id': rec.product_id.product_tmpl_id.id,
            #     })
            # price_unit = rec.price_unit
            # if rec.product_uom and seller.product_uom != rec.product_uom:
            #     price_unit = rec.product_uom._compute_price(
            #         price_unit, seller.product_uom)

            # if net_price_installed:
            #     seller.net_price = rec.order_id.currency_id._convert(
            #         price_unit, seller.currency_id, rec.order_id.company_id,
            #         rec.order_id.date_order or fields.Date.today())
            # else:
            #     seller.price = rec.order_id.currency_id._convert(
            #         price_unit, seller.currency_id, rec.order_id.company_id,
            #         rec.order_id.date_order or fields.Date.today())

    @api.model
    def control_fecha_recepcion(self):
        purchase_order = self.env["purchase.order"].search([('state','=','purchase')])

        # cant. de días antes de la fecha prevista para registrar la actividad
        dias_registrar_actividad = 2
        activity_type_id = self.env.ref('pronto.confirmar_fecha_recepcion')
        model_stock_picking = self.env.ref('purchase.model_purchase_order')

        for po in purchase_order:
            for pol in po.order_line:
                # todavía queda pendientes
                if pol.product_qty != pol.qty_received:
                    # delta = picking.scheduled_date.date() - fields.Date.context_today(self)
                    delta = pol.date_planned.date() - fields.Date.context_today(self)
                    if delta.days == dias_registrar_actividad or delta.days <= 0:

                        summary = activity_type_id.summary + ' - ' + str(pol.product_id.default_code)
                        res_id = pol.order_id.id
                        
                        # verficar si tiene actividad de ese tipo
                        activity = self.env['mail.activity'].search([('res_model_id','=',model_stock_picking.id),
                        ('activity_type_id','=',activity_type_id.id),
                        ('res_id','=',res_id),
                        ('summary','=',summary),])
                        
                        if not activity:
                            # self._schedule_activity(activity_type_id, pol.order_id, pol.product_id)
                            vals = {
                                'activity_type_id': activity_type_id.id,
                                'date_deadline': fields.Date.today(),
                                'summary': summary,
                                'user_id': 8, # marcos
                                'res_id': res_id,
                                'res_model_id': model_stock_picking.id,
                                'res_model':  model_stock_picking.model
                            }
                            # mail_activity_quick_update=True para que no le muestre un aviso al usuario. t-70
                            self.env['mail.activity'].with_context(mail_activity_quick_update=True).create(vals)