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

class CovidFollowup(models.Model):
    '''CovidFollowup'''
    _name = 'school.covid_followup'
    _description = 'Repodrint of a COVID follow up'
    _inherit = ['mail.thread']
    
    _order = 'name asc, reporting_date desc'
    
    name = fields.Char(string="Name", related='student_id.name', store=True)
    
    author_id = fields.Many2one('res.users', string='Author')
    student_id = fields.Many2one('res.partner', string='Student', required=True, ondelete='restrict')
    reporting_date = fields.Date(string='Reporting Date')
    
    reporting_type = fields.Selection([
            ('nothing','Rien à signaler'),
            ('low_risk', 'Placement en bas risque'),
            ('high_risk', 'Placement en haut risque'),
            ('test_done', 'Test COVID fait'),
            ('result_neg', 'Résultat test COVID négatif'),
            ('result_pos', 'Résultat test COVIDE positif'),
            ('start_quar', 'Début quarantaine'),
            ('end_quar', 'Fin quarantaine'),
            ('other', 'Autre'),
        ], string='Reporting Type', index=True, default='nothing',
        track_visibility='onchange',
        copy=False,
        help="")
    
    details = fields.Char(string="Details")
    
    probing_doc = fields.Many2many('ir.attachment', 'probing_doc_attachment_rel', 'covid_followup_id',
                                      'attachment_id', 'Probing docs',
                                      help="You may attach files to this followup")
    
    @api.model
    def default_get(self, fds):
        res = super(CovidFollowup, self).default_get(fds)
        if 'author_id' in fds:
            res['author_id'] = self.env.user.id
        if 'reporting_date' in fds:
            res['reporting_date'] = fields.Date.today()
        return res
        
class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'
    
    covid_followup_ids = fields.One2many('school.covid_followup', 'student_id', string='COVID Followups', copy=False)
    
    last_covid_followup_date = fields.Date(string='Last Contact Date', compute='_compute_last_covid_followup', store=True)
    
    last_covid_followup_type = fields.Selection([
            ('nothing','Rien à signaler'),
            ('low_risk', 'Placement en bas risque'),
            ('high_risk', 'Placement en haut risque'),
            ('test_done', 'Test COVID fait'),
            ('result_neg', 'Résultat test COVID négatif'),
            ('result_pos', 'Résultat test COVIDE positif'),
            ('start_quar', 'Début quarantaine'),
            ('end_quar', 'Fin quarantaine'),
            ('other', 'Autre'),
        ], string='Last Contact Type', compute='_compute_last_covid_followup', store=True)
    
    @api.depends('covid_followup_ids')
    def _compute_last_covid_followup(self):
        for rec in self:
            last_covid_followup = rec.covid_followup_ids.sorted(key=lambda r: r.reporting_date)[-1]
            self.last_covid_followup_date = last_covid_followup.reporting_date
            self.last_covid_followup_type = last_covid_followup.reporting_type