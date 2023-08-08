import logging
import json

_logger = logging.getLogger(__name__)

from odoo import tools, api, fields, models, _

class Menu(models.Model):
    _inherit = 'website.menu'

    public = fields.Boolean("Public", default=True)
    student = fields.Boolean("Student", default=False)
    teacher = fields.Boolean("Teacher", default=False)
    employee = fields.Boolean("Employee", default=False)

    @api.model
    def init_school_portal_menu(self):
        _logger.info("Init school portal menu")
        # menus = self.env["website.menu"].search([])

        website_id = self.env["website"].get_current_website().id
        default_main_menu_id = self.env["website.menu"].search([('parent_id', '=', None), ('website_id', '=', website_id)]).id

        parent = self.env['website.menu'].create({
                'name': "Réservations",
                'url': None,
                'page_id': None,
                'parent_id': default_main_menu_id,
                'website_id': website_id,
                'public' : False,
                'student' : True,
                'teacher' : True,
                'employee' : True,
            })
        
        self.env['website.menu'].create({
                'name': "Mes réservations",
                'url': "/reservations/mes-reservations",
                'page_id': None,
                'parent_id': parent.id,
                'website_id': website_id,
                'public' : False,
                'student' : True,
                'teacher' : True,
                'employee' : True,
            })
        
        self.env['website.menu'].create({
                'name': "Créer une réservation",
                'url': "/reservations/creation",
                'page_id': None,
                'parent_id': parent.id,
                'website_id': website_id,
                'public' : False,
                'student' : True,
                'teacher' : True,
                'employee' : True,
            })
        
        self.env.cr.commit()