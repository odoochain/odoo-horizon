# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2023 ito-invest.lu
#                       Jerome Sonnet <jerome.sonnet@ito-invest.lu>
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

from odoo import api, fields, models, _
from odoo.exceptions import MissingError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class BCEDPersonne(models.TransientModel):
    _name = "school.bced_personne_wizard"
    _description = "BCED Personne Wizard"
    
    student_id = fields.Many2one('res.partner', string='Student', required=True)

    student_name = fields.Char(related='student_id.name', string='Name', readonly=True)
    student_image_512 = fields.Binary('Image', attachment=True, related='student_id.image_512', readonly=True)
    student_niss = fields.Char(related='student_id.reg_number', string='Niss', readonly=True)
    student_lastname = fields.Char(related='student_id.lastname', string='Last Name', readonly=True)
    student_birthdate = fields.Date(related='student_id.birthdate', string='Birth Date', readonly=True)

    state = fields.Selection([('no_bced', 'No BCED'), ('bced', 'Has BCED')], string='State', default='draft')

    @api.model
    def default_get(self, fields):
        res = super(BCEDPersonne, self).default_get(fields)
        student_id = self.env['res.partner'].browse(self.env.context.get('active_id'))
        if student_id:
            ws = self.env['school.webservice'].search([('name', '=', 'bced_personne')], limit=1)
            data = ws.getPerson(student_id)
            if data.status and data.status['code'] == 'SOA5100000':
                res['state'] = 'no_bced'
            else:
                res['state'] = 'bced'
        return res
        
    def action_retrieve_bced_personne(self):
        self.ensure_one()
       
        return True

    def action_create_bced_personne(self):
        self.ensure_one()
       
        return True