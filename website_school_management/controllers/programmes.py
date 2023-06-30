# -*- encoding: utf-8 -*-

import logging

from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug, unslug

_logger = logging.getLogger(__name__)

class programmes(http.Controller):
    @http.route(['/programmes'], type='http', auth='public', website = True)
    def programmes(self, redirect=None, **post):
        param = ""
        searchParams = [('state', '=', 'published')]
        if (post.get('operation') != 'clear'): # http.request.params.get('operation') == post.get('operation')
            # TODO étoffer la recherche
            param = post.get('s')
            if (isinstance(param, str)):
                searchParams = [
                    ('state', '=', 'published'), 
                    '|', ('name', 'ilike', param), ('year_short_name', 'ilike', param)
                    ]

        programs = request.env['school.program'].sudo().search(searchParams,order="domain_name, cycle_id, name ASC")
        program_list = []

        for program in programs:
            program_list.append({
                'program' : program,
                'slug_id' : slug(program),
            })
        values = {
            'program_list': program_list,
            'root': '/programmes',
            'param' : param
        }
        return request.render("website_school_management.programmes", values)