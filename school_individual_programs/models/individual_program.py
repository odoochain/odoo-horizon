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

from openerp import api, fields, models, tools, _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class IndividualProgram(models.Model):
    '''Individual Program'''
    _name='school.individual_program'
    _description='Individual Program'
    _inherit = ['mail.thread']
    
    _order = 'name'

    active = fields.Boolean(string='Active', help="The active field allows you to hide the course group without removing it.", default=True, copy=False)

    name = fields.Char(compute='_compute_name',string='Name', readonly=True, store=True)
    
    year_id = fields.Many2one('school.year', string='Registration Year', default=lambda self: self.env.user.current_year_id)
    
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]", required=True)
    student_name = fields.Char(related='student_id.name', string="Student Name", readonly=True, store=True)
    
    image = fields.Binary('Image', attachment=True, related='student_id.image')
    image_medium = fields.Binary('Image', attachment=True, related='student_id.image_medium')
    image_small = fields.Binary('Image', attachment=True, related='student_id.image_small')
    
    source_program_id = fields.Many2one('school.program', string="Source Program", ondelete="restrict")
    
    cycle_id = fields.Many2one('school.cycle', related='source_program_id.cycle_id', string='Cycle', store=True, readonly=True)
    
    speciality_id = fields.Many2one('school.speciality', related='source_program_id.speciality_id', string='Speciality', store=True, readonly=True)
    #domain_id = fields.Many2one(related='speciality_id.domain_id', string='Domain',store=True)
    #section_id = fields.Many2one(related='speciality_id.section_id', string='Section',store=True)
    #track_id = fields.Many2one(related='speciality_id.track_id', string='Track',store=True)
    
    @api.depends('cycle_id.name','speciality_id.name','student_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s - %s" % (rec.student_id.name,rec.cycle_id.name,rec.speciality_id.name)
    