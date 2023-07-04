# -*- encoding: utf-8 -*-

import logging

from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug, unslug

_logger = logging.getLogger(__name__)

class programmes(http.Controller):
    @http.route([
        '/programmes',
        '/programmes/<string:domain>',
        '/programmes/<string:domain>/<string:speciality>',
        '/programmes/<string:domain>/<string:speciality>/<string:year>',
        '/programmes/<string:domain>/<string:speciality>/<string:year>/<string:cycle_type>',
        '/programmes/<string:domain>/<string:speciality>/<string:year>/<string:cycle_type>/<string:cycle>',
        '/programmes/<string:domain>/<string:speciality>/<string:year>/<string:cycle_type>/<string:cycle>/<string:title>',
        ], type='http', auth='public', website = True)
    def programmes_list(self, domain = None, speciality = None, year = None, cycle_type = None, cycle = None, title = None, **post):
        
        searchParams = [('state', '=', 'published'), ('domain_name', '!=', None)]
        segment = 0

        if (domain):
            searchParams.append(('domain_slug', '=', domain))
            segment = 1
            if (speciality):
                searchParams.append(('speciality_slug', '=', speciality))
                segment = 2
                if (year):
                    searchParams.append(('year_name', '=', year))
                    segment = 3
                    if (cycle_type):
                        searchParams.append(('cycle_grade_slug', '=', cycle_type))
                        segment = 4
                        if (cycle):
                            searchParams.append(('cycle_name_slug', '=', cycle))  
                            segment = 5
                            if (title):
                                searchParams.append(('title_slug', '=', title))
                                segment = 6

        programs = request.env['school.program'].sudo().search(searchParams,order="domain_name, cycle_id, name ASC")

        if (len(programs) == 1):
            # TODO à adapter
            # TODO redirect si URI courant <> URI du programme
            program = programs[0]
            values = {
                'program': program,
                'slug_id' : program.id,
            }
            return request.render("website_school_management.program_details", values)
        elif (len(programs) > 0):
            breadcrumb = [{'uri' : "",'name' : "Tous les programmes"}]
            if (domain):
                breadcrumb.append({'uri' : programs[0].domain_slug,'name' : programs[0].domain_name})
                if (speciality):
                    breadcrumb.append({'uri' : programs[0].domain_slug + "/" + programs[0].speciality_slug,'name' : programs[0].speciality_name})
                    if (year):
                        breadcrumb.append({'uri' : programs[0].domain_slug + "/" + programs[0].speciality_slug + "/" + programs[0].year_name,'name' : programs[0].year_name})
                        if (cycle_type):
                            breadcrumb.append({'uri' : programs[0].domain_slug + "/" + programs[0].speciality_slug + "/" + programs[0].year_name + "/" + programs[0].cycle_grade_slug,'name' : programs[0].cycle_grade},)
                            if (cycle):
                                breadcrumb.append({'uri' : programs[0].domain_slug + "/" + programs[0].speciality_slug + "/" + programs[0].year_name + "/" + programs[0].cycle_grade_slug + "/" + programs[0].cycle_name_slug,'name' : programs[0].cycle_name})
                                if (title):
                                    breadcrumb.append({'uri' : programs[0].program_uri,'name' : programs[0].title})

            options = []
            
            if (segment == 0):
                for program in programs:
                    option = {'uri' : program.domain_slug, 'name' : program.domain_name}
                    if (option not in options):
                        options.append(option)
            elif (segment == 1):
                for program in programs:
                    option = {'uri' : domain + '/' + program.speciality_slug, 'name' : program.speciality_name}
                    if (option not in options):
                        options.append(option)            
            elif (segment == 2):
                for program in programs:
                    option = {'uri' : domain + '/' + speciality + '/' + program.year_name, 'name' : program.year_name}
                    if (option not in options):
                        options.append(option)            
            elif (segment == 3):
                for program in programs:
                    option = {'uri' : domain + '/' + speciality + '/' + year + '/' +program.cycle_grade_slug, 'name' : program.cycle_grade}
                    if (option not in options):
                        options.append(option) 
            elif (segment == 4):
                for program in programs:
                    option = {'uri' : domain + '/' + speciality + '/' + year + '/' + cycle_type + '/' + program.cycle_name_slug, 'name' : program.cycle_name}
                    if (option not in options):
                        options.append(option)             
            elif (segment == 5):
                for program in programs:
                    option = {'uri' : domain + '/' + speciality + '/' + year + '/' + cycle_type + '/' + cycle + '/' + program.title_slug, 'name' : program.title}
                    if (option not in options):
                        options.append(option)             

            program_list = []
            for program in programs:
                program_list.append({
                    'program' : program,
                })
            values = {
                'program_list': program_list,
                'root': '/programmes',
                'breadcrumb' : breadcrumb,
                'options' : options
            }
            return request.render("website_school_management.programmes", values)
        else:
            # TODO à adapter
            return request.redirect("/error")