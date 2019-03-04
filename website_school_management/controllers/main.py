# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

import werkzeug

from openerp.addons.website.models.website import slug, unslug

from openerp import http
from openerp.addons.web.controllers.main import CSVExport

from openerp.http import request, serialize_exception
from openerp import tools
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class csv_school_management(CSVExport):

    @http.route('/web/export/blocs', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        data = """{
                  "model": "school.bloc",
                  "fields": [
                    {
                      "name": "id",
                      "label": "External ID"
                    },
                    {
                      "name": "year_id/name",
                      "label": "Année scolaire/Nom"
                    },
                    {
                      "name": "domain_id/name",
                      "label": "Domaine/Nom"
                    },
                    {
                      "name": "name",
                      "label": "Nom"
                    },
                    {
                      "name": "level",
                      "label": "Niveau"
                    },
                    {
                      "name": "track_id/name",
                      "label": "Option/Nom"
                    },
                    {
                      "name": "track_id/saturn_code",
                      "label": "Option/Saturn Code"
                    },
                    {
                      "name": "total_credits",
                      "label": "Total des ECTS"
                    },
                    {
                      "name": "total_weight",
                      "label": "Total de la pondération"
                    },
                    {
                      "name": "total_hours",
                      "label": "Total des Heures"
                    },
                    {
                      "name": "program_id/id",
                      "label": "Programme/Identifiant"
                    }
                  ],
                  "ids": false,
                  "domain": [
                    [
                      "year_sequence",
                      "=",
                      "current"
                    ],
                    [
                      "title",
                      "ilike",
                      "master"
                    ]
                  ],
                  "context": {
                    "lang": "fr_BE",
                    "tz": "Europe/Brussels",
                    "uid": 1,
                    "params": {
                      "action": 109
                    }
                  },
                  "import_compat": true
                }"""
        return self.base(data, token)

class website_portal_school_management(http.Controller):

    @http.route(['/program'], type='http', auth='public')
    def program(self, redirect=None, **post):
        programs = request.env['school.program'].sudo().search([('state', '=', 'published')],order="domain_id, cycle_id, name ASC")
        program_list = []
        for program in programs:
            program_list.append({
                'program' : program,
                'slug_id' : slug(program),
            })
        values = {
            'program_list': program_list,
        }
        return request.render("website_school_management.program", values)
        
    @http.route(['/program/domain/<domain_id>'], type='http', auth='public')
    def program_domain(self, domain_id, redirect=None, **post):
        _, domain_id = unslug(domain_id)
        programs = request.env['school.program'].sudo().search([('state', '=', 'published'),('domain_id','=',domain_id)],order="domain_id, cycle_id, name ASC")
        program_list = []
        for program in programs:
            program_list.append({
                'program' : program,
                'slug_id' : slug(program),
            })
        values = {
            'program_list': program_list,
        }
        return request.render("website_school_management.program", values)
    
    @http.route(['/program/<program_id>'], type='http', auth='public')
    def program_details(self, program_id, redirect=None, **post):
        _, program_id = unslug(program_id)
        program = request.env['school.program'].sudo().search([('id','=',program_id)])
        if program :
            values = {
                'program': program,
                'slug_id' : program_id,
            }
            return request.render("website_school_management.program_details", values)
        else :
            raise werkzeug.exceptions.HTTPException(description='Unkown program.')
        
    @http.route(['/course/<course_id>'], type='http', auth='public')
    def course(self, course_id, redirect=None, **post):
        _, course_id = unslug(course_id)
        course_docs = request.env['school.course_documentation'].sudo().search([('state', '=', 'published'),'|',('course_ids','=',course_id),('course_id','=',course_id)],order="author_id")
        if course_docs:
            values = {
                'docs': course_docs[0],
            }
            return request.render("school_course_description.report_course_documentation_content", values)
        else:
            return request.render("school_course_description.report_course_documentation_no_content", [])
            
            
    @http.route(['/course_group/<course_group_id>'], type='http', auth='public')
    def course_group(self, course_group_id, redirect=None, **post):
        _, course_group_id = unslug(course_group_id)
        course_group_id = request.env['school.course_group'].sudo().browse([course_group_id])
        if course_group_id:
            values = {
                'docs': course_group_id,
            }
            return request.render("school_course_description.report_course_group_documentation_content", values)
        else:
            return request.render("school_course_description.report_course_group_documentation_no_content", [])
        
    @http.route(['/print_program/<model("school.program"):program>'], type='http', auth='public')
    def print_program(self, program, redirect=None, **post):
        
        report_obj = request.registry['report']
        cr, uid, context = request.cr, request.uid, request.context
        reportname = 'school_management.report_program_details_content'
        
        pdf = report_obj.get_pdf(cr, uid, [program.id], reportname, data=None, context=None)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)