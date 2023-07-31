from odoo import http
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)

class WebCRLGController(http.Controller):
    
    @http.route(['/etudiants-info'], type='http', auth='user', website=True)
    def student_info(self, redirect=None, **post):
        return request.render("website_crlg_portal.valves_etudiants_crlg")
        
    @http.route(['/professeurs-info'], type='http', auth='user', website=True)
    def teacher_info(self, redirect=None, **post):
        if (request.env.user.teacher or request.env.is_admin()):
            return request.render("website_crlg_portal.valves_professeurs_crlg")
        else :
            return request.redirect('/')