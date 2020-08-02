##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _get_moves_to_assign_domain(self):
        # de esta manera desactivo la parte del planificador que
        # que reserva el stock
        return [('id','=',0)]

    @api.model
    def run_smart_scheduler(self, picking_id = 0):

        dias_registrar_actividad = int(self.env['ir.config_parameter'].search([('key','=','pronto.dias_registrar_actividad')]).value)
        dias_reservar = int(self.env['ir.config_parameter'].search([('key','=','pronto.dias_reservar')]).value)

        if picking_id:            
            archivo_log = '/opt/odoo/run_smart_scheduler__log-OE-{}.txt'.format(picking_id)

            picking_ids = list()
            picking_ids.append(self.env['stock.picking'].browse(picking_id))
        else:
            archivo_log = '/opt/odoo/run_smart_scheduler__log-{}.txt'.format(fields.Date.context_today(self))
            # ATENCION: puede estar 'assigned' y que todavía le falte una parte para reservar
            picking_ids = self.env['stock.picking'].search([
                                ('state','in',['confirmed','assigned']),
                                ('picking_type_code','=','outgoing'),
                                ('scheduled_date','<=',fields.Date.context_today(self) + timedelta(days=dias_registrar_actividad))])

        log = open(archivo_log,'w')
        log.write('{} \n'.format(fields.Datetime.now()))
        log.close()

        model_stock_picking = self.env.ref('stock.model_stock_picking')
        activity_type_id = self.env.ref('pronto.contactar_cliente_reserva_stock')
        for picking in picking_ids:
            linea1 = 'picking: {} - Cliente: {}'.format(picking.id,picking.partner_id.name.encode('utf-8'))

            delta = picking.scheduled_date.date() - fields.Date.context_today(self)

            # si el picking tiene actividades del tipo contactar_cliente_reserva_stock
            # esto te trae las que no estan como "done" porque esas estan marcadas como active=False
            activity = self.env['mail.activity'].search([('res_model_id','=',model_stock_picking.id),
                    ('activity_type_id','=',activity_type_id.id),
                    ('res_id','=',picking.id)])

            if not activity:
                # que registre actividad si:
                    # faltan exactamente 12 (dias_registrar_actividad) dias hasta la fecha prevista.
                    # o si la fecha prevista está en el pasado
                # ojo! si un pedido recien se confirma con fecha prevista dentro de 12 días, va a registrar una
                # actividad. Ent me fijo que la fecha de creación del picking no sea hoy.
                if (delta.days == dias_registrar_actividad or delta.days < 0) and picking.create_date.date() != fields.Date.context_today(self):    
                    activity = picking._schedule_activity()
                    line = linea1 + ' - Actividad'
                    self.escribir_log(archivo_log, line)

            # esta dentro del periodo de reserva? 10 días antes
            if delta.days <= dias_reservar:
                estados_moves = picking.mapped('move_ids_without_package.state')
                if 'partially_available' in estados_moves or 'confirmed' in estados_moves:
                    picking.action_assign()

                productos = []
                for move in picking.move_ids_without_package:
                    if move.state in ['confirmed','partially_available']:
                        productos.append(move.product_id.id)                      
                
                if productos:
                    line = linea1 + ' - No es posible reservar: {}'.format(productos)
                else:
                    line = linea1 + ' - Completamente reservado'

            else:
                line = linea1 + ' - Proximo a reserva automatica'

            self.escribir_log(archivo_log, line)

        return

    @api.model
    def escribir_log(self,archivo_log,line):
        with open(archivo_log, 'a') as the_file:
            the_file.write(line + '\n')
    