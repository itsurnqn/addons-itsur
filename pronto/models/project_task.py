##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models, _
from odoo.osv import expression

class ProjectTask(models.Model):
    _inherit = 'project.task'

    referente_id = fields.Many2one(
        comodel_name='res.users',
        string='Referente',        
    )
