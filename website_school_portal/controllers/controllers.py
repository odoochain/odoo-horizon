from odoo import http
from odoo.http import request
from odoo.http import (Response)

import logging

_logger = logging.getLogger(__name__)

class WebSchoolPortalController(http.Controller):

    ###########################################################
    #                       SNIPPETS                          #
    ###########################################################

    # Renvoie le template du snippet et ses éventuelles données
    @http.route(['/hz_generic_insert_snippet/<string:template>'], type="json", auth='public', website=True)
    def generic_insert_snippet(self, template, **kw):
        return http.request.env['ir.ui.view']._render_template("website_school_portal." + template, self.get_data_for_template(template))
    
    # Renvoie les données à afficher dans un template
    def get_data_for_template(self, template):
        data = None
        if template == "hz_horizon_access":
            data = {
                'request': http.request
            }
        return data
    
    ###########################################################
    #                     RESPONSIVE                          #
    ###########################################################

    @http.route('/mes-donnees/mon-programme', type='http', auth='user', website=True) # TODO >>> website_school_portal >>> controller mes-donnees >>> route /mes-donnees/mon-programme
    def responsive_blocs(self, debug=False, **k):
        if not (request.env.user.partner_id.student or request.env.is_admin()):
            return Response(template='website_school_portal.hz_page_403', status=403)
        values = {
            'user': request.env.user,
            'blocs': request.env['school.individual_bloc'].sudo().search([('student_id','=',request.env.user.partner_id.id),('year_id','=',request.env.user.current_year_id.id)]),
            'display_results': request.env['ir.config_parameter'].sudo().get_param('school.display.results', '0'),
        }
        return request.render('website_school_portal.hz_blocs', values)
    
    @http.route('/mes-donnees/mes-documents', type='http', auth='user', website=True) # TODO >>> website_school_portal >>> controller mes-donnees >>> route /mes-donnees/mes-documents
    def responsive_documents(self, debug=False, **k):
        if not (request.env.user.partner_id.student or request.env.is_admin()):
            return Response(template='website_school_portal.hz_page_403', status=403)
        user = request.env.user
        partner_id = user.partner_id
        values = {
            'user': user,
            'official_document_ids' : partner_id.official_document_ids,
            'blocs' : request.env['school.individual_bloc'].sudo().search([('student_id','=',request.env.user.partner_id.id),('year_id','=',request.env.user.current_year_id.id)]),
        }
        return request.render('website_school_portal.hz_documents', values)