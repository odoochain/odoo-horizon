import logging

_logger = logging.getLogger(__name__)

from odoo import tools, api, fields, models, _

class Menu(models.Model):
    _inherit = 'website.menu'

    public = fields.Boolean("Public", default=True)
    student = fields.Boolean("Student", default=False)
    teacher = fields.Boolean("Teacher", default=False)
    employee = fields.Boolean("Employee", default=False)