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
    
    def action_open_form(self):
        self.ensure_one()
        for cg in self.ind_course_group_ids :
            if cg.state in ['2_candidate','1_confirmed','0_valuated']:
                valuation_followup = self.env['school.valuation_followup'].search([('individual_course_group_id','=',cg.id)])
                if valuation_followup :
                    return {
                        'type': 'ir.actions.act_window',
                        'name': _(valuation_followup.name),
                        'res_model': valuation_followup._name,
                        'res_id': valuation_followup.id,
                        'view_mode': 'form',
                    }
        return {
            'type': 'ir.actions.act_window',
            'name': _(self.name),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
        }
    
    def action_reject_course_group(self):
        for rec in self :
            for cg in rec.individual_course_group.ids :
                if cg.state in ['2_candidate','1_confirmed']:
                    cg.write({'state','3_rejected'})
        return {
            'type': 'ir.actions.act_view_reload',
        }
    
    def action_candidate_valuate_course_group(self):
        for rec in self :
            valuated_cg = self.env['school.individual_course_group'].create({
                'valuated_program_id' : rec.program_id.id,
                'source_course_group_id' : rec.course_group_id.id,
                'state' : '2_candidate',
                'year_id' : self.env.user.current_year_id.id
            })
            rec.program_id.valuated_course_group_ids |= valuated_cg
            self.env['school.valuation_followup'].create({
                'individual_course_group_id' : valuated_cg.id
            })
        return {
            'type': 'ir.actions.act_view_reload',
        }
    
class ValuationFollwup(models.Model):
    '''Valuation Follow Up'''
    _name='school.valuation_followup'
    _description='Valuation Followup'
    _inherit = ['mail.thread','school.uid.mixin']
    
    individual_course_group_id = fields.Many2one('school.individual_course_group', string='Individual Course Group', required=True)
    
    name = fields.Char(related="individual_course_group_id.name", string="Name")
    
    title = fields.Char(related="individual_course_group_id.title", string="Title")
    
    student_id = fields.Many2one('res.partner', related='individual_course_group_id.valuated_program_id.student_id', string="Student")
    
    image_1920 = fields.Binary('Image', attachment=True, related='student_id.image_1920')
    image_128 = fields.Binary('Image', attachment=True, related='student_id.image_128')
    
    responsible_id = fields.Many2one('res.partner', related='individual_course_group_id.responsible_id', string="Responsible")
    
    responsible_decision = fields.Selection([
            ('accept','Accepted'),
            ('reject','Rejected')
    ], string="Responsible Decision", default="reject", tracking=True)

    state = fields.Selection([
            ('10_irregular','Irregular'),
            ('9_draft','Draft'),
            ('7_failed', 'Failed'),
            ('6_success', 'Success'),
            ('5_progress','In Progress'),
            ('3_rejected','Rejected'),
            ('2_candidate','Candidate'),
            ('1_confirmed','Candidate'),
            ('0_valuated', 'Valuated'),
        ], string='Status', related="individual_course_group_id.state", tracking=True)
    
    administration_comments = fields.Text(string="Administration Comments", tracking=True)
    
    responsible_comments = fields.Text(string="Responsible Comments", tracking=True)
    
    attachment_ids = fields.Many2many('ir.attachment','valuations_ir_attachment_rel', 'valuation_id','ir_attachment_id', 'Attachments', tracking=True)
    
    def action_revert_to_candidate(self):
        for rec in self :
            rec.individual_course_group_id.write({
                'state' : '2_candidate'
            }) 
    
    def action_confirm_valuate_course_group(self):
        for rec in self :
            rec.individual_course_group_id.write({
                'state' : '1_confirmed'
            }) 
            composer_form_view_id = self.env.ref('mail.email_compose_message_wizard_form').id

            template_id = self.env.ref('school_valuations.email_template_valuation_teacher').id
    
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'view_id': composer_form_view_id,
                'target': 'new',
                'context': {
                    'default_composition_mode': 'mass_mail' if len(self.ids) > 1 else 'comment',
                    'default_res_id': self.ids[0],
                    'default_model': self._name,
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'website_sale_send_recovery_email': True,
                    'active_ids': self.ids,
                },
            }
            
    def action_valuate_course_group(self):
        for rec in self :
            rec.individual_course_group_id.write({
                'state' : '0_valuated'
            }) 
            
    def action_reject_course_group(self):
        for rec in self :
            rec.individual_course_group_id.write({
                'state' : '3_rejected'
            }) 