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

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class Deliberation(models.Model):
    '''Deliberation'''
    _name = 'school.deliberation'
    _description = 'Manage deliberation process'
    _inherit = ['school.year_sequence.mixin']
    
    state = fields.Selection([
            ('draft','Draft'),
            ('active', 'Active'),
            ('archived', 'Archived'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when a new deliberation is created and not running yet.\n"
             " * The 'Active' status is when a deliberation is ready to be processed.\n"
             " * The 'Archived' status is used when a deliberation is obsolete and shall be archived.")
        
    year_id = fields.Many2one('school.year', required=True, string="Year")
    
    session = fields.Selection(
        ([('first','First'),('sec','Second'),('third','Third')]),
        string='Session',
        required=True)
    
    date = fields.Date(required=True, string="Date")
    
    name = fields.Char(required=True, string="Title")
    
    secretary_id = fields.Many2one('res.partner', required=True, domain=[('employee','=',True)])
    
    individual_program_ids = fields.Many2many('school.individual_program', 'school_deliberation_program_rel', 'deliberation_id', 'program_id', string='Programs',domain=[('state','=','progress')])
    
    individual_program_count = fields.Integer(string='Programs Count', compute="_compute_counts")
    
    individual_bloc_ids = fields.Many2many('school.individual_bloc', 'school_deliberation_bloc_rel', 'deliberation_id', 'bloc_id', string='Blocs',domain=[('state','=','progress')])
    
    individual_bloc_count = fields.Integer(string='Blocs Count', compute="_compute_counts")
    
    participant_ids = fields.Many2many('res.partner', 'school_deliberation_participants_rel', 'deliberation_id', 'partner_id', string='Particpants')
    
    excused_participant_ids = fields.Many2many('res.partner', 'school_deliberation_excused_part_rel', 'deliberation_id', 'partner_id', string='Excused Particpants')
    
    @api.onchange('individual_bloc_ids')
    def _on_update_individual_bloc_ids(self):
        for rec in self:
            rec.individual_program_ids = rec.individual_bloc_ids.search([('is_final_bloc','=',True)]).mapped('program_id')
    
    @api.onchange('excused_participant_ids')
    def _on_update_participant_ids(self):
        for rec in self:
            rec.participant_ids = rec.participant_ids - rec.excused_participant_ids
    
    def _compute_counts(self):
        for rec in self:
            rec.individual_program_count = len(rec.individual_program_ids)
            rec.individual_bloc_count = len(rec.individual_bloc_ids)
    
    def to_draft(self):
        return self.write({'state': 'draft'})

    def activate(self):
        return self.write({'state': 'active'})

    def archive(self):
        return self.write({'state': 'archived'})
        
    def action_populate_participants(self):
        self.ensure_one()
        return self.write({'participant_ids' : [(6, 0, self._compute_all_responsibles().ids)]})
        
    def _compute_all_responsibles(self):
        all_responsibles = self.env['res.partner']
        for bloc in self.individual_bloc_ids :
            all_responsibles |= bloc.get_all_responsibles()
        for program in self.individual_program_ids :
            all_responsibles |= program.get_all_responsibles()
        return all_responsibles
    
    def action_open_deliberation_bloc(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deliberate Blocs',
            'res_model': 'school.individual_bloc',
            'domain': [('deliberation_ids', 'in', self.id )],
            'view_mode': 'kanban,deliberation',
            'search_view_id' : (self.env.ref('school_deliberation_base.view_deliberation_bloc_filter').id,),
            'views': [[self.env.ref('school_deliberation_base.deliberation_bloc_kanban_view').id,'kanban'],[self.env.ref('school_deliberation_base.deliberation_bloc_view').id,'deliberation']],
            'context': {'deliberation_id':self.id},
        }
        
class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'
    
    deliberation_ids = fields.Many2many('school.deliberation', 'school_deliberation_bloc_rel', 'bloc_id', 'deliberation_id', string='Deliberations', readonly=True)
    
    all_responsible_ids = fields.Many2many('res.partner', compute='_compute_all_responsibles')
    
    def _compute_all_responsibles(self):
        for rec in self:
            rec.all_responsible_ids = rec.get_all_responsibles()

    def close_deliberate_bloc(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deliberate Blocs',
            'res_model': 'school.individual_bloc',
            'domain': [('deliberation_ids', 'in', self._context.get('deliberation_id') )],
            'view_mode': 'kanban',
            'search_view_id' : (self.env.ref('school_deliberation_base.view_deliberation_bloc_filter').id,),
            'views': [[self.env.ref('school_deliberation_base.deliberation_bloc_kanban_view').id,'kanban']],
        }
        
    def action_deliberate_course_group(self):
        self.ensure_one()
        course_group_deliberation_ids = self.env['school.course_group_deliberation'].search([
            ['deliberation_id','=',self._context['deliberation_id']],
            ['course_group_id','=',self._context['default_course_group_id']]
        ])
        if course_group_deliberation_ids :
            return {
                'type': 'ir.actions.act_window',
                'name': 'Deliberate Course Group',
                'target': 'new',
                'flags': { 'action_buttons': True, 'headless': True },
                'res_model':  'school.course_group_deliberation',
                'res_id': course_group_deliberation_ids[0].id,
                'context': self._context,
                'views': [[False, 'form']],
            }
        else :
            return {
                'type': 'ir.actions.act_window',
                'name': 'Deliberate Course Group',
                'target': 'new',
                'flags': { 'action_buttons': True, 'headless': True },
                'res_model':  'school.course_group_deliberation',
                'context': self._context,
                'views': [[False, 'form']],
            }
            
class CourseGroupDeliberation(models.Model):
    '''Deliberation'''
    _name = 'school.course_group_deliberation'
    _description = 'Manage deliberation of a course group'
    
    deliberation_id = fields.Many2one('school.deliberation', required=True)
    
    course_group_id = fields.Many2one('school.individual_course_group', required=True)
    
    course_ids = fields.One2many('school.individual_course', related='course_group_id.course_ids', string='Courses')
    
    comments = fields.Char(string='Comments')

    is_deliberated_to_acquiered = fields.Boolean(string='Is deliberated to acquiered')
    
    participant_ids = fields.Many2many('res.partner', related='course_group_id.bloc_id.all_responsible_ids', string='Particpants')
    
    image = fields.Binary('Image', attachment=True, related='course_group_id.student_id.image')
    
    image_medium = fields.Binary('Image', attachment=True, related='course_group_id.student_id.image_medium')
    
    image_small = fields.Binary('Image', attachment=True, related='course_group_id.student_id.image_small')
    
    name = fields.Char(string='Name', related='course_group_id.title')
    
    final_result_disp = fields.Char(string='Final Result Display', related='course_group_id.final_result_disp')
    
    student_name = fields.Char(string='Student', related='course_group_id.student_id.name')
    
    @api.onchange('is_deliberated_to_acquiered')
    def _onchange_is_deliberated_to_acquiered(self):
        if self.is_deliberated_to_acquiered :
            if self.deliberation_id.session == 'first' :
                self.course_group_id.set_deliberated_to_ten(session=1)
            else :
                self.course_group_id.set_deliberated_to_ten(session=2)
            return {
                'value': {'final_result_disp': '10'}
            }
        else :
            self.course_group_id.first_session_deliberated_result_bool = False
            self.course_group_id.first_session_deliberated_result = False
            self.course_group_id.first_session_deliberated_result_bool = False
            self.course_group_id.first_session_deliberated_result = False