from odoo import http

import logging

_logger = logging.getLogger(__name__)

class WebCRLGPortalController(http.Controller):

    ###########################################################
    #                       SNIPPETS                          #
    ###########################################################

    # Renvoie le template du snippet et ses éventuelles données
    @http.route(['/hz_generic_insert_snippet/<string:template>'], type="json", auth='public', website=True)
    def generic_insert_snippet(self, template, **kw):
        return http.request.env['ir.ui.view']._render_template("website_crlg_portal." + template, self.get_data_for_template(template))
    
    # Renvoie les données à afficher dans un template
    def get_data_for_template(self, template):
        data = None
        if template == "hz_connexion_snippet":
            data = {
                'request': http.request
            }
        return data