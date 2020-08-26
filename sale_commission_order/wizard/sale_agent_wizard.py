from odoo import models, fields, api


class SaleAgentWizard(models.TransientModel):
    _name = "sale.order.agent.wizard"
    _description = "Sale order Agent Wizard"

    agent = fields.Many2one(string="Agente",comodel_name="res.partner",domain=[('agent', '=', True)])

    @api.multi
    def confirm(self):
        self.ensure_one()
        order = self.env['sale.order'].browse(
            self._context.get('active_id', False))

        for line in order.order_line:
            if self.agent:
                vals = {
                    'agent': self.agent.id,
                    'commission': self.agent.commission.id,
                    'object_id': line.id
                }
                line.agents.create(vals)
            else:
                line.agents.unlink()
        
        return True