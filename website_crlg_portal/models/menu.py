import logging

_logger = logging.getLogger(__name__)

from odoo import tools, api, fields, models, _

class Menu(models.Model):
    _inherit = 'website.menu'

    @api.model
    def init_crlg_menu(self):
        _logger.info("Init crlg menu")
        menus = self.env["website.menu"].search([])
        for record in menus:
            if record.url == '/etudiants-info':
                record.public = False
                record.student = True
                record.teacher = True
            elif record.url == '/professeurs-info':
                record.public = False
                record.teacher = True