##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountPaymentPlanTarjeta(models.Model):
	_name = 'account.payment.plan.tarjeta'
	_description = 'Plan de tarjeta de credito'

	name = fields.Char('Nombre')

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_credit_card = fields.Boolean('Es tarjeta de credito',related='journal_id.is_credit_card')
    nro_cupon = fields.Char('Nro Cupon')
    nro_tarjeta = fields.Char('Nro Tarjeta')
    cant_cuotas = fields.Integer('Cuotas')
    plan_tarjeta_id = fields.Many2one('account.payment.plan.tarjeta',string='Plan Tarjeta', ondelete='Restrict')
    nro_lote = fields.Integer('Nro lote')

	# @api.one
    # @api.constrains('nro_cupon','nro_tarjeta','plan_tarjeta_id')
    @api.constrains('nro_cupon','nro_lote')
    def _check_pago_tarjeta(self):
        if self.is_credit_card:
            if (not self.nro_cupon) or (not self.nro_lote) or (not self.plan_tarjeta_id):
                raise ValidationError("Debe ingresar los datos de pago de tarjeta")