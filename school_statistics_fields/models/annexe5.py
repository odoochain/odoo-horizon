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

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class IndividualBloc(models.Model):
    _inherit = 'school.individual_bloc'
    
    is_annexe5_validated = fields.Boolean(string="Validated for Saturn")
    

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'

    student_annexe5_entry_ids = fields.One2many('school.student_annexe5_entry', 'student_id', string="Student Annexe 5", track_visibility='onchange')
    
class StudentAnnexe5Entry(models.Model):
    '''Student Annexe 5 Entry'''
    _name = 'school.student_annexe5_entry'
    
    year_id = fields.Many2one('school.year', string="Year", required=True)
    
    student_id = fields.Many2one('res.partner', string="Student", required=True)
    
    activite = fields.Selection([('ETU','Etudes'),('TRAV','Travail'),('CHOM','Chômage'),('ETR','Etranger'),('AUT','Autre')]
                                , string="Activité", required=True)
    
    code_saturn = fields.Many2one('school.speciality', string="Code Saturn", required=False)
    
    type = fields.Selection([('U','U'),('HE','HE'),('ESA','ESA'),('PSU','PSU'),('HE','HE'),('ESA','ESA'),('PS','PS')], string="Type", requiered=False)
    
    inscription = fields.Selection([('B1','B1'), ('B2','B2'), ('B3','B3'), ('M1','M1'), ('M2','M2'), ('SP','SP'), ('1A1C','1A1C')], string="Inscription", requiered=False)
    
    resultat = fields.Selection([('R','Réussi'),('E','Echec')], string='Résultat', requiered=False)
    
    pae_num = fields.Integer(string='PAE Num', requiered=False)
    
    pae_den = fields.Integer(string='PAE Den', requiered=False)