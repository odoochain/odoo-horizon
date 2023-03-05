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
import json

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)

class Registration(models.Model):
    '''Registration'''
    _name = 'school.registration'
    _description = 'Registration of new/existing students'
    _inherit = ['mail.thread','school.uid.mixin','school.year_sequence.mixin','school.open.form.mixin']
    
    year_id = fields.Many2one('school.year', required=True, string="Year")
    
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
    
    contact_form_data = fields.Text(related='contact_form_id.submission_data')
    
    def action_fill_contact_with_form(self):
        pass
    
    def to_draft(self):
        return self.write({'state': 'draft'})

    def activate(self):
        return self.write({'state': 'active'})

    def archive(self):
        return self.write({'state': 'archived'})
        
    def _format_date(self, date_str):
        day, month, year = date_str.split('/')
        return f"{year}-{month}-{day}"
        
    def _extract_base64_data_from_data_url(self,data_url):
        # split the data URL into its components
        parts = data_url.split(",")
        # extract the base64-encoded data from the URL
        base64_data = parts[1]
        return base64_data
        
    def action_fill_partner_date(self):
        for rec in self:
            contact_data = json.load(rec.contact_form_data)
            rec.lastname = contact_data['nom']
            rec.firstname = contact_data['prenom']
            rec.gender = contact_data['sexe']
            rec.birthdate_date = fields.Datetime.from_string(rec._format_date(contact_data['dateDeNaissance']))
            rec.birthplace = contact_data['lieuDeNaiss']
            rec.lastname = contact_data['nom']
            rec.birthcountry = self.env['res.country'].browse(contact_data['brith_country'])
            #rec.nationalites
            rec.image_1920 = tools.base64_to_image(rec._extract_base64_data_from_data_url(contact_data['photo']['url']))
            rec.street = contact_data['adresseLigne']
            rec.city = contact_data['ville']
            rec.zip= contact_data['codePostal']
            rec.country = self.env['res.country'].browse(contact_data['country'])
            rec.street = contact_data['adresseLigne1']
            rec.city = contact_data['ville1']
            rec.zip= contact_data['codePostal1']
            rec.country = self.env['res.country'].browse(contact_data['country1'])
            rec.phone = contact_data['telephonePortab']
            rec.email_personnel = contact_data['email']
            rec.reg_number = contact_data['numeroDeRegistreNational']
        
    def action_open_student(self):
        self.ensure_one()
        return {
            'name': 'Student',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'res_id': self.student_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
        
    _sql_constraints = [
        ('student_year_uniq', 'unique (student_id, year_id)', "Registration already exists for that student in this year!"),
    ]
        
class Form(models.Model):
    '''Individual Bloc'''
    _inherit = 'formio.form'

    def write(self, vals):
        res = super(Form, self).write(vals)
        if 'submission_data' in vals and 'state' in vals and vals['state'] == 'COMPLETE' :
            self._create_or_update_registration()
        return res
        
    def _create_or_update_registration(self):
        registration_open_year_id = int(self.env['ir.config_parameter'].sudo().get_param('school.registration_open_year_id', '0'))
        for rec in self:
            if rec.name == 'new_contact' and rec.submission_partner_id :
                reg = self.env['school.registration'].search([['year_id','=',registration_open_year_id],['student_id','=',rec.submission_partner_id.id]])
                if reg :
                    reg.contact_form_id = rec
                else :
                    self.env['school.registration'].create({
                        'year_id' : registration_open_year_id,
                        'student_id' : rec.submission_partner_id.id,
                        'contact_form_id' : rec.id
                    })