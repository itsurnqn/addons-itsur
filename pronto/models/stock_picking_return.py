# -*- coding: utf-8 -*-
# Part of Odoo. See ICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class ReturnPickingPronto(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        # import pdb; pdb.set_trace()

        for return_line in self.product_return_moves:                  

            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))

            entrada_salida = return_line.move_id.picking_id.picking_type_id.code
            
            if entrada_salida == 'incoming':
                # estoy en una entrada y voy a generar una salida                    
                # controlo que no salga más de lo que se pidió
                sale_id = return_line.move_id.picking_id.sale_id.id

                order_line = self.env['sale.order.line'].search(['&',('order_id','=',sale_id),('product_id','=',return_line.product_id.id)])

                cant_pedida = 0
                cant_entregada = 0
                for ol in order_line:
                    cant_pedida = cant_pedida + ol.product_uom_qty
                    cant_entregada = cant_entregada + ol.qty_delivered

                cant_pendiente = cant_pedida - cant_entregada

                if return_line.quantity > cant_pendiente:
                    raise UserError(_("Intenta retirar más de lo pedido."))
        
        # esta heredando desde stock_ux. ahí _create_returns retorna estos
        # dos valores. por eso se hace así
        new_picking, pick_type_id = super()._create_returns()

        return new_picking, pick_type_id
