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
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)


class IndividualCourseSummary(models.Model):
    '''IndividualCourse Summary'''
    _inherit = 'school.individual_course_summary'
    
    def action_candidate_valuate_course_group(self):
        ret = super(IndividualCourseSummary, self).action_valuate_course_group()
        for rec in self :
            valuated_cg = self.env['school.individual_course_group'].search([
                ['valuated_program_id','=',rec.program_id.id],
                ['source_course_group_id','=',rec.course_group_id.id]
            ])
            self.env['school.valuation_followup'].create({
                'individual_course_group_id' : valuated_cg.id
            })
        return ret
    
class ValuationFollwup(models.Model):
    '''Valuation Follow Up'''
    _name='school.valuation_followup'
    _description='Valuation Followup'
    _inherit = ['mail.thread','school.uid.mixin']
    
    individual_course_group_id = fields.Many2one('school.individual_course_group', string='Individual Course Group', required=True)
    
    title = fields.Char(related="individual_course_group_id.title", string="Title")
    
    student_id = fields.Many2one('res.partner', related='individual_course_group_id.student_id', string="Student")
    
    responsible_id = fields.Many2one('res.partner', related='individual_course_group_id.responsible_id', string="Responsible")
    
    state = fields.Selection([
            ('10_irregular','Irregular'),
            ('9_draft','Draft'),
            ('7_failed', 'Failed'),
            ('6_success', 'Success'),
            ('5_progress','In Progress'),
            ('2_candidate','Candidate'),
            ('1_confirmed','Candidate'),
            ('0_valuated', 'Valuated'),
        ], string='Status', related="individual_course_group_id.state")
    
    administration_comments = fields.Text(string="Administration Comments")
    
    responsible_comments = fields.Text(string="Responsible Comments")
    
    attachment_ids = fields.Many2many('ir.attachment','valuations_ir_attachment_rel', 'valuation_id','ir_attachment_id', 'Attachments')