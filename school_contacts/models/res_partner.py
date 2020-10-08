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
import threading
import re

import openerp
from openerp import tools, api, fields, models, _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class school_year_sequence_mixin(models.AbstractModel):
    _name = "school.year_sequence.mixin"

    year_sequence = fields.Selection([
        ('current','Current'),
        ('previous','Previous'),
        ('next','Next'),
        ], string="Year Sequence", compute="_compute_year_sequence", search="_search_year_sequence")
        
    def _compute_year_sequence(self):
        for item in self:
            current_year_id = self.env.user.current_year_id
            if current_year_id.id == item.year_id.id:
                item.year_sequence = 'current'
            if current_year_id.previous.id == item.year_id.id:
                item.year_sequence = 'previous'
            if current_year_id.next.id == item.year_id.id:
                item.year_sequence = 'next'
        
    def _search_year_sequence(self, operator, value):
        current_year_id = self.env.user.current_year_id
        year_ids = []
        if 'current' in value:
            year_ids.append(current_year_id.id)
        if 'previous' in value:
            year_ids.append(current_year_id.previous.id)
        if 'next' in value:
            year_ids.append(current_year_id.next.id)
        return [('year_id','in',year_ids)]

class Year(models.Model):
    '''Year'''
    _name = 'school.year'
    _order = 'name'
    name = fields.Char(required=True, string='Name', size=15)
    short_name = fields.Char(required=True, string='Short Name', size=5)
    
    previous = fields.Many2one('school.year', string='Previous Year')
    next = fields.Many2one('school.year', string='Next Year')
    
class Users(models.Model):
    '''Users'''
    _inherit = ['res.users']
    
    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on notification_email_send
            and alias fields. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super(Users, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.extend(['current_year_id'])
        # duplicate list to avoid modifying the original reference
        self.SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        self.SELF_READABLE_FIELDS.extend(['current_year_id'])
    
    current_year_id = fields.Many2one('school.year', string="Current Year")

class StudentHistoryEntry(models.Model):
    '''Student History Entry'''
    _name = 'school.student_history_entry'
    
    year_id = fields.Many2one('school.year', string="Year", required=True)
    student_id = fields.Many2one('res.partner', string="Student", required=True)
    activite = fields.Selection([
        ('0','Enseignement supérieur de la fédération Wallonie Bruxelle'),
        ('1','Enseignement secondaire non obligatoire (année préparatoire à l’enseignement supérieur, 4e cycle du secondaire, ...)'),
        ('2','Haute École de la Fédération Wallonie‐Bruxelles ou germanophone'),
        ('3','Université de la Fédération Wallonie‐Bruxelles'),
        ('4','Institut supérieur d''Architecture de la Fédération Wallonie‐Bruxelles'),
        ('5','École supérieure des Arts de la Fédération Wallonie‐Bruxelles'),
        ('6','Enseignement supérieur de promotion sociale de la Fédération Wallonie‐Bruxelles'),
        ('7','Enseignement supérieur de la Communauté flamande'),
        ('8','Enseignement supérieur à l''étranger'),
        ('9','Travail rémunéré'),
        ('10','Chômage'),
        ('11','Autre (année sabbatique, préparation à l''enseignement supérieur autre que dans le cadre de l''enseignement secondaire,...)'),
        ], string="Activité", required=True)
    etablissement_id = fields.Many2one('school.stat_etablissement', string="Etablissement")
    domain_id = fields.Many2one('school.stat_domain', string="Domaine")
    annee = fields.Selection([
            ('11','1re Bac'),
            ('12','2e Bac'),
            ('13','3e Bac'),
            ('14','4e Bac'),
            ('21','1re Master'),
            ('22','2e Master'),
            ('23','3e Master'),
            ('24','4e Master'),
            ('31','1re Spécialisation'),
            ('32','2e Spécialisation'),
            ('40','Doctorat'),
            ('99','Autres (CAPAES, AESS, Année préparatoire, etc.)'),
        ], string="Année")
    resultat = fields.Selection([
            ('1','Réussite'),
            ('2','Refusé'),
        ],string="Résultat")

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'
    
    student = fields.Boolean("Student",default=False)
    teacher = fields.Boolean("Teacher",default=False)
    employee = fields.Boolean("Employee",default=False)
    
    initials = fields.Char('Initials')
    
    nationality_id = fields.Many2one("res.country", "Nationality")
    
    image = fields.Binary('Image', oldname='image_1920')
    image_medium = fields.Binary('Image', oldname='image_512')
    image_small = fields.Binary('Image', oldname='image_128')
    
    @api.constrains('initials')
    def _check_initials(self):
        self.ensure_one()
        if self.initials and not re.match('([A-Z]\.,)*([A-Z]\.)?',self.initials):
            raise UserError(_("Please encode initials as eg X.,V.,T."))
    
    birthplace = fields.Char('Birthplace')
    birthcountry = fields.Many2one('res.country', 'Birth Country', ondelete='restrict')
    phone2 = fields.Char('Phone2')
    title = fields.Selection([('Mr', 'Monsieur'),('Mme', 'Madame'),('Mlle', 'Mademoiselle')])
    marial_status = fields.Selection([('M', 'Maried'),('S', 'Single')])
    registration_date = fields.Date('Registration Date')
    email_personnel = fields.Char('Email personnel')
    reg_number = fields.Char('Registration Number')
    mat_number = fields.Char('Matricule Number')
    
    student_historic_entry_ids = fields.One2many('school.student_history_entry', 'student_id', string="Student History Entries", track_visibility='onchange')
    
    # Secondary adress

    secondary_street = fields.Char('Street')
    secondary_street2 = fields.Char('Street2')
    secondary_zip = fields.Char('Zip', size=24, change_default=True)
    secondary_city = fields.Char('City')
    secondary_state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    secondary_country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')

    teacher_curriculum_vitae = fields.Html('Curriculum Vitae')