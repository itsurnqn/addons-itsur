##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.task'

    complexity_level_id = fields.Many2one(
        comodel_name='project.task.complexity.level',
        string='Nivel de complejidad',
        copy=False
    )