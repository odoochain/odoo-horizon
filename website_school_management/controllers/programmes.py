# -*- encoding: utf-8 -*-

import logging

from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug, unslug

_logger = logging.getLogger(__name__)

# Gestion des différentes routes pour les programmes de cours
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
        # Préparation des paramètres de recherche
        searchParams = [('state', '=', 'published'), ('domain_name', '!=', None)]
        # searchParams = [('domain_name', '!=', None)]
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
        # Requête
        programs = request.env['school.program'].sudo().search(searchParams,order="domain_name, cycle_id, name ASC")

        # Si un seul résultat
        if (len(programs) == 1):
            route = request.httprequest.path
            program = programs[0]

            # Si la route ne correspond pas à celle du programme : redirection
            if (route != program.program_uri):
                return request.redirect(program.program_uri)

            # Récupération du breadcrump
            breadcrumb = self.get_breadcrumb(program, segment)

            template = "website_school_management.programme_fiche"
            values = {
                'program': program,
                'breadcrumb' : breadcrumb,
            }
        # Si plusieurs résultats
        elif (len(programs) > 0):
            # Récupération du breadcrump
            breadcrumb = self.get_breadcrumb(programs[0], segment)
            # Récupération des options
            options = self.get_options(programs, segment)

            if (len(options) == 1):
                return request.redirect(options[0]['uri'])

            template = "website_school_management.programmes"
            values = {
                'program_list': programs,
                'breadcrumb' : breadcrumb,
                'options' : options,
            }
        # Si 0 résultat
        else :
            template = "website_school_management.programmes"
            values = {
                'program_list': [],
                'message' : 'Aucun résultat pour cette recherche.'
            }

        return request.render(template, values)
    
    # Génération du breadcrumb
    def get_breadcrumb (self, program, segment):
        breadcrumb = [{'uri' : "/programmes/", 'name' : "Tous les programmes"}]
        if (segment >= 1):
            breadcrumb.append({'uri' : '/programmes/' + program.domain_slug, 'name' : program.domain_name})
            if (segment >= 2):
                breadcrumb.append({'uri' : '/programmes/' + program.domain_slug + "/" + program.speciality_slug, 'name' : program.speciality_name})
                if (segment >= 3):
                    breadcrumb.append({'uri' : '/programmes/' + program.domain_slug + "/" + program.speciality_slug + "/" + program.year_name, 'name' : program.year_name})
                    if (segment >= 4):
                        breadcrumb.append({'uri' : '/programmes/' + program.domain_slug + "/" + program.speciality_slug + "/" + program.year_name + "/" + program.cycle_grade_slug, 'name' : program.cycle_grade},)
                        if (segment >= 5):
                            breadcrumb.append({'uri' : '/programmes/' + program.domain_slug + "/" + program.speciality_slug + "/" + program.year_name + "/" + program.cycle_grade_slug + "/" + program.cycle_name_slug, 'name' : program.cycle_name})
                            if (segment >= 6):
                                breadcrumb.append({'uri' : '/programmes/' + program.program_uri, 'name' : program.title})
        return breadcrumb
    
    # Génération des options
    def get_options (self, programs, segment):
        options = []
        if (segment == 0):
            for program in programs:
                option = {'uri' : '/programmes/' + program.domain_slug, 'name' : program.domain_name}
                if (option not in options):
                    options.append(option)
        elif (segment == 1):
            for program in programs:
                option = {'uri' : '/programmes/' + program.domain_slug + '/' + program.speciality_slug, 'name' : program.speciality_name}
                if (option not in options):
                    options.append(option)            
        elif (segment == 2):
            for program in programs:
                option = {'uri' : '/programmes/' + program.domain_slug + '/' + program.speciality_slug + '/' + program.year_name, 'name' : program.year_name}
                if (option not in options):
                    options.append(option)            
        elif (segment == 3):
            for program in programs:
                option = {'uri' : '/programmes/' + program.domain_slug + '/' + program.speciality_slug + '/' + program.year_name + '/' + program.cycle_grade_slug, 'name' : program.cycle_grade}
                if (option not in options):
                    options.append(option) 
        elif (segment == 4):
            for program in programs:
                option = {'uri' : '/programmes/' + program.domain_slug + '/' + program.speciality_slug + '/' + program.year_name + '/' + program.cycle_grade_slug + '/' + program.cycle_name_slug, 'name' : program.cycle_name}
                if (option not in options):
                    options.append(option)             
        elif (segment == 5):
            for program in programs:
                option = {'uri' : '/programmes/' + program.domain_slug + '/' + program.speciality_slug + '/' + program.year_name + '/' + program.cycle_grade_slug + '/' + program.cycle_name_slug + '/' + program.title_slug, 'name' : program.title}
                if (option not in options):
                    options.append(option)
        return options
    
    ##############
    # TEMPORAIRE #
    ##############

    # Gestion de la génération du PDF d'un programme de cours
    @http.route('/impression_programme/<int:id>', type='http', auth="public", website=True, sitemap=False)
    def print_program_pdf(self, id, **kw):
        if id:
            try:
                id = int(id) # Conversion en int obligatoire car variable get de type str
                if (not self.program_exists(id)):
                    return request.redirect('/error')
                else:
                    pdf = request.env.ref('website_school_management.action_impression_programme_id')._render_qweb_pdf("website_school_management.action_impression_programme_id", [id])[0]
            except ValueError:
                return request.redirect('/error')

        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return http.request.make_response(pdf, headers=pdfhttpheaders)
    
    # Vérifie si un programme en particulier existe
    def program_exists(self, id):
        program = request.env['school.program'].sudo().search([('id','=',id)])
        if program is None or program.id != id:
            return False
        else:
            return True
        
    # Gestion de la route d'un cours
    @http.route(['/cours/<string:course_slug>'], type='http', auth='public',  website=True)
    def cours(self, course_slug, redirect=None, **post):
        _, course_id = unslug(course_slug)
        course_docs = request.env['school.course_documentation'].sudo().search([('state', '=', 'published'),'|',('course_ids','=',course_id),('course_id','=',course_id)],order="author_id")
        if course_docs:
            values = {
                'course_docs': course_docs,
            }
            return request.render("website_school_management.cours_fiche", values)
        else:
            return request.render("website_school_management.cours_fiche_vide", [])
            
    # Gestion de la route d'un groupe de cours    
    @http.route(['/groupe_de_cours/<string:course_group_slug>'], type='http', auth='public', website=True)
    def groupe_de_cours(self, course_group_slug, redirect=None, **post):
        _, course_group_id = unslug(course_group_slug)
        course_group = request.env['school.course_group'].sudo().search([('id', '=', course_group_id)])
        if course_group:
            values = {
                'course_group': course_group,
            }
            return request.render("website_school_management.groupe_de_cours_fiche", values)
        else:
            return request.render("website_school_management.groupe_de_cours_fiche_vide", [])
    
    

        