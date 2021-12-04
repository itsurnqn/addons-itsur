from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PaymentGroupCancel(models.TransientModel):
    _name = 'payment.group.cancel'
    _description = 'Cancelar recibo'

    payment_group_id = fields.Many2one('account.payment.group',"Recibo")
    cancel_reason_note = fields.Char("Detalle el motivo de la cancelación")
    
    @api.model
    def default_get(self, field_names):
        defaults = super(PaymentGroupCancel, self).default_get(field_names)
        defaults['payment_group_id'] = self.env.context['active_id']
        return defaults    

    def do_cancel(self):
        rec = self.payment_group_id
        rec.write({'cancel_reason_note': self.cancel_reason_note})
        for move in rec.move_line_ids.mapped('move_id'):
            rec.matched_move_line_ids.remove_move_reconcile()
            # TODO borrar esto si con el de arriba va bien
            # if rec.to_pay_move_line_ids:
            #     move.line_ids.remove_move_reconcile()
        rec.payment_ids.cancel()
        rec.payment_ids.write({'invoice_ids': [(5, 0, 0)]})
        rec.write({'state': 'cancel'})        

        # raise UserError("recibo {0}".format(self.payment_group_id.name))