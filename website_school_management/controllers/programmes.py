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
        '/programmes/<string:year>',
        '/programmes/<string:year>/<string:domain>',
        '/programmes/<string:year>/<string:domain>/<string:track>',
        '/programmes/<string:year>/<string:domain>/<string:track>/<string:speciality>',
        '/programmes/<string:year>/<string:domain>/<string:track>/<string:speciality>/<string:cycle_type>',
        '/programmes/<string:year>/<string:domain>/<string:track>/<string:speciality>/<string:cycle_type>/<string:cycle>',
        '/programmes/<string:year>/<string:domain>/<string:track>/<string:speciality>/<string:cycle_type>/<string:cycle>/<string:title>',
        ], type='http', auth='public', website = True, sitemap=False)
    def programmes(self, year = None, domain = None, track = None, speciality = None, cycle_type = None, cycle = None, title = None, **post):
        # Préparation des paramètres de recherche
        searchParams = [('state', '=', 'published'), ('domain_name', '!=', None), ('track_name', '!=', None)]
        # searchParams = [('domain_name', '!=', None), ('track_name', '!=', None)]
        segment = 0

        if (year):
            searchParams.append(('year_name', '=', year))
            segment = 1
            if (domain):
                searchParams.append(('domain_slug', '=', domain))
                segment = 2
                if (track):
                    searchParams.append(('track_slug', '=', track))
                    segment = 3
                    if (speciality):
                        searchParams.append(('speciality_slug', '=', speciality))
                        segment = 4
                        if (cycle_type):
                           searchParams.append(('cycle_grade_slug', '=', cycle_type))
                           segment = 5
                           if (cycle):
                               searchParams.append(('cycle_name_slug', '=', cycle))  
                               segment = 6
                               if (title):
                                   searchParams.append(('title_slug', '=', title))
                                   segment = 7
        # Requête
        programs = request.env['school.program'].sudo().search(searchParams,order='year_short_name ASC, domain_name ASC, cycle_grade_order ASC, cycle_name ASC, name ASC')

        # Si un seul résultat
        if (len(programs) == 1):
            route = request.httprequest.path
            program = programs[0]

            # Si la route ne correspond pas à celle du programme : redirection
            return request.redirect('/programme/' + slug(program))
        # Si plusieurs résultats
        elif (len(programs) > 0):
            # Récupération du breadcrump
            breadcrumb = self._get_breadcrumb(programs[0], segment)
            # Récupération des options
            options = self._get_options(programs, segment)

            template = "website_school_management.programmes_liste"
            values = {
                'program_list': programs,
                'breadcrumb' : breadcrumb,
                'options' : options,
            }
            return request.render(template, values)
        # Si 0 résultat
        else :
            return request.render('website.404')
    
    @http.route(['/programme/<string:program_slug>'], type='http', auth='public',  website=True, sitemap=True)
    def programme(self, program_slug, redirect=None, **post):
        _, program_id = unslug(program_slug)
        program = request.env['school.program'].sudo().search([('state', '=', 'published'),('id', '=', program_id)])
        if program:
            # Préparation du breadcrump
            breadcrumb = self._get_breadcrumb(program, 7)
            template = 'website_school_management.programme_fiche'
            values = {
                'program': program,
                'breadcrumb' : breadcrumb,
            }
            return request.render(template, values)
        else:
            return request.render('website.404')


    # Génération du breadcrumb
    def _get_breadcrumb (self, program, segment):
        breadcrumb = [{'uri' : "/programmes/", 'name' : "Tous les programmes"}]
        if (segment >= 1 and program.year_name):
            breadcrumb.append({'uri' : '/programmes/' + program.year_name, 'name' : program.year_name})
            if (segment >= 2 and program.domain_name):
                breadcrumb.append({'uri' : '/programmes/' + program.year_name + "/" + program.domain_slug, 'name' : program.domain_name})
                if (segment >= 3 and program.track_name):
                    breadcrumb.append({'uri' : '/programmes/' + program.year_name + "/" + program.domain_slug + "/" + program.track_slug, 'name' : program.track_name})
                    if (segment >= 4 and program.speciality_name):
                        breadcrumb.append({'uri' : '/programmes/' + program.year_name + "/" + program.domain_slug + "/" + program.track_slug + "/" + program.speciality_slug, 'name' : program.speciality_name})
                        if (segment >= 5 and program.cycle_grade):
                            breadcrumb.append({'uri' : '/programmes/' + program.year_name + "/" + program.domain_slug + "/" + program.track_slug + "/" + program.speciality_slug + "/" + program.cycle_grade_slug, 'name' : program.cycle_grade},)
                            if (segment >= 6 and program.cycle_name):
                                breadcrumb.append({'uri' : '/programmes/' + program.year_name + "/" + program.domain_slug + "/" + program.track_slug + "/" + program.speciality_slug + "/" + program.cycle_grade_slug + "/" + program. cycle_name_slug, 'name' : program.cycle_name})
        if (segment >= 7):
            breadcrumb.append({'uri' : '/programme/' + slug(program), 'name' : program.title})
        return breadcrumb
    
    # Génération des options
    def _get_options (self, programs, segment):
        options = []
        if (segment == 0):
            for program in programs:
                option = {'uri' : '/programmes/' + program.year_name, 'name' : program.year_name}
                if (option not in options):
                    options.append(option)
        if (segment == 1):
            for program in programs:
                option = {'uri' : '/programmes/' + program.year_name + '/' + program.domain_slug, 'name' : program.domain_name}
                if (option not in options):
                    options.append(option)
        elif (segment == 2):
            for program in programs:
                option = {'uri' : '/programmes/' + program.year_name + '/' + program.domain_slug + '/' + program.track_slug, 'name' : program.track_name}
                if (option not in options):
                    options.append(option)            
        elif (segment == 3):
            for program in programs:
                option = {'uri' : '/programmes/' + program.year_name + '/' + program.domain_slug + '/' + program.track_slug + '/' + program.speciality_slug, 'name' : program.speciality_name}
                if (option not in options):
                    options.append(option)            
        elif (segment == 4):
            for program in programs:
                option = {'uri' : '/programmes/' + program.year_name + '/' + program.domain_slug + '/' + program.track_slug + '/' + program.speciality_slug + '/' + program.cycle_grade_slug, 'name' : program.cycle_grade}
                if (option not in options):
                    options.append(option) 
        elif (segment == 5):
            for program in programs:
                option = {'uri' : '/programmes/' + program.year_name + '/' + program.domain_slug + '/' + program.track_slug + '/' + program.speciality_slug + '/' + program.cycle_grade_slug + '/' + program.cycle_name_slug, 'name' : program.cycle_name}
                if (option not in options):
                    options.append(option)             
        elif (segment == 6):
            for program in programs:
                option = {'uri' : '/programmes/' + program.year_name + '/' + program.domain_slug + '/' + program.track_slug + '/' + program.speciality_slug + '/' + program.cycle_grade_slug + '/' + program.cycle_name_slug + '/' + program.title_slug, 'name' : program.title}
                if (option not in options):
                    options.append(option)
        return options
    
    ##############
    # TEMPORAIRE #
    ##############

    # Gestion de la génération du PDF d'un programme de cours
    @http.route('/impression_programme/<string:program_slug>', type='http', auth="public", website=True, sitemap=False)
    def print_program_pdf(self, program_slug, **kw):
        _, program_id = unslug(program_slug)
        program = request.env['school.program'].sudo().search([('state', '=', 'published'),('id', '=', program_id)])
        if program:
            pdf = request.env.ref('website_school_management.action_impression_programme_id')._render_qweb_pdf("website_school_management.action_impression_programme_id", [program.id])[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return http.request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.render('website.404')
    
    # Gestion de la route d'un cours
    @http.route(['/cours/<string:course_slug>'], type='http', auth='public',  website=True, sitemap=True)
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
    
    

        