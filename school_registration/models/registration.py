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
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)

class Registration(models.Model):
    '''Registration'''
    _name = 'school.registration'
    _description = 'Registration of new/existing students'
    _inherit = ['mail.thread','school.uid.mixin','school.year_sequence.mixin','school.open.form.mixin']
    
    student_id = fields.Many2one('res.partner', string='Student')
    
    name = fields.Char(related='student_id.name')
    image_1920 = fields.Binary('Image', attachment=True, related='student_id.image_1920')
    image_128 = fields.Binary('Image', attachment=True, related='student_id.image_128')
    
    state = fields.Selection([
            ('draft','Draft'),
            ('active', 'Active'),
            ('archived', 'Archived'),
        ], string='Status', index=True, readonly=True, default='draft',
        copy=False,
        help=" * The 'Draft' status is used when a new registration is created and not running yet.\n"
             " * The 'Active' status is when a registration is ready to be processed.\n"
             " * The 'Archived' status is used when a registration is obsolete and shall be archived.")
             
    contact_form_id = fields.Many2one('formio.form', string='Contact Form')
    
    def action_fill_contact_with_form(self):
        pass
    
    def to_draft(self):
        return self.write({'state': 'draft'})

    def activate(self):
        return self.write({'state': 'active'})

    def archive(self):
        return self.write({'state': 'archived'})
        
    _sql_constraints = [
        ('student_year_uniq', 'unique (student_id, year_id)', "Registration already exists for that student in this year!"),
    ]
        
class Form(models.Model):
    '''Individual Bloc'''
    _inherit = 'formio.form'

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Form, self).create(vals_list)
        records._create_or_update_registration()
        
    def _create_or_update_registration(self):
        for rec in self:
            if rec.name == 'new_contact':
                reg = self.env['school.registration'].search([['year_id','=',],['student_id','=',]])