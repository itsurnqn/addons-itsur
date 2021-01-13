##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProjectTaskComplexityLevel(models.Model):
    _name = 'project.task.complexity.level'
    _description = 'Nivel de complejidad de tareas'
    # _order = 'sequence asc'
    _order = 'project_id,sequence'

    name = fields.Char(required=True)

    description = fields.Html()

    project_id = fields.Many2one('project.project',
                                 string="Project",
                                 index=True)
    
    sequence = fields.Integer()

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('project.task.complexity.level') or 0
        vals['sequence'] = seq
        return super(ProjectTaskComplexityLevel, self).create(vals)