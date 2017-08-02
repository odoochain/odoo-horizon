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
from openerp.exceptions import MissingError

_logger = logging.getLogger(__name__)

class SplitUEWizard(models.TransientModel):
    _name = "school.split_cg_wizard"
    _description = "Split Course Group Wizard"
    
    source_course_group_id = fields.Many2one('school.course_group', string="Source Course Group")
    target_first_course_group_id = fields.Many2one('school.course_group', string="Source Course Group")
    target_second_course_group_id = fields.Many2one('school.course_group', string="Source Course Group")
    
    target_first_course_ids = fields.One2many(related='target_first_course_group_id.course_ids')
    target_second_course_ids = fields.One2many(related='target_second_course_group_id.course_ids')
    
    @api.onchange('source_course_group_id')
    def on_change_source_course_group_id(self):
        self.update({
            'target_first_course_group_id': self.source_course_group_id.copy(),
            'target_second_course_group_id': self.source_course_group_id.copy(),
        })
    
    @api.multi
    def on_confirm(self):
        self.ensure_one()
        for bloc in self.source_course_group_id.bloc_ids:
            pass
        return {'type': 'ir.actions.act_window_close'}
        
    @api.multi
    def on_cancel(self):
        self.ensure_one()
        self.target_first_course_group_id.unlink()
        self.target_second_course_group_id.unlink()
        return {'type': 'ir.actions.act_window_close'}