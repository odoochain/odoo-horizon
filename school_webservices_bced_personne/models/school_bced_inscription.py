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
import logging.config
import base64
import os
import io
from datetime import datetime, timedelta
import uuid
from lxml import etree

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

def getFRDescription(value):
    return [x for x in value['description'] if x['language'] == 'fr'][0]['_value_1']

class BCEDInscription(models.Model):
    _name = 'school.bced.inscription'
    _description = 'BCED Inscription'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    reference = fields.Char(string='Reference')
    legal_context = fields.Char(string='Legal Context', required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def action_submit(self):
        ws = self.env['school.webservice'].search([('name', '=', 'bced_inscription')], limit=1)
        for rec in self:
            res = ws.publishInscription(rec)
            if res:
                rec.reference = res['inscriptionReference']
                rec.partner_id.inscription_id = rec.id
            
    def action_revoke(self):
        for rec in self:
            # TODO : implement revoke
            pass

    def action_update_partner_information(self):
        ws = self.env['school.webservice'].search([('name', '=', 'bced_personne')], limit=1)
        for rec in self:
            if not rec.reference:
                raise UserError(_('No reference found for this partner, please submit first to BCDE service.'))
            # We are registered so we can proceed with data usage
            data = ws.getPerson(rec.partner_id.reg_number)
            if data :
                self.partner_id.reg_number = data['personNumber']
                self.partner_id.firstname = data['name']['firstName'][0]
                self.partner_id.lastname = ' '.join(data['name']['lastName'])
                if len(data['name']['firstName']) > 1 :
                    self.partner_id.initials = ','.join(map(lambda x: x[0], data['name']['firstName'][1:]))
                else:
                    self.partner_id.initials = ''
                if data['gender'] :
                    self.partner_id.gender = 'male' if data['gender']['code']['_value_1'] == 'M' else 'female'
                if data['nationalities'] :
                    # TODO : no nationality in BCDE for now
                    pass
                for address in data['addresses']['address']:
                    # Diplomatic is for foreigner
                    if address['addressType'] == 'Diplomatic':
                        self.partner_id.street = address['plainText'][0]['_value_1']
                        self.partner_id.street2 = ''
                        self.partner_id.zip = ''
                        self.partner_id.city = ''
                        self.partner_id.state_id = False
                        self.partner_id.country_id = self.env['res.country'].search([('code', '=', address['country'][0]['code']['_value_1'])], limit=1).id
                    if address['addressType'] == 'Residential':
                        street_name = getFRDescription(address['street'])
                        if address['boxNumber'] :
                            self.partner_id.street = ' '.join([street_name,address['houseNumber'],address['boxNumber']])
                        else :
                            self.partner_id.street = ' '.join([street_name,address['houseNumber']])
                        self.partner_id.street2 = ''
                        self.partner_id.zip = address['postCode']['code']['_value_1']
                        self.partner_id.city = getFRDescription(address['municipality'])
                        self.partner_id.state_id = False
                        self.partner_id.country_id = self.env['res.country'].search([('code', '=', address['country'][0]['code']['_value_1'])], limit=1).id
                    elif address['addressType'] == 'PostAddress':
                        street_name = getFRDescription(address['street'])
                        if address['boxNumber'] :
                            self.partner_id.secondary_street = ' '.join([street_name,address['houseNumber'],address['boxNumber']])
                        else :
                            self.partner_id.secondary_street = ' '.join([street_name,address['houseNumber']])
                        self.partner_id.secondary_street2 = ''
                        self.partner_id.secondary_zip = address['postCode']['code']['_value_1']
                        self.partner_id.secondary_city = getFRDescription(address['municipality'])
                        self.partner_id.secondary_state_id = False
                        self.partner_id.secondary_country_id = self.env['res.country'].search([('code', '=', address['country'][0]['code']['_value_1'])], limit=1).id
                self.partner_id.birthdate_date = fields.Date.to_date(data['birth']['officialBirthDate'])
                if data['birth']['birthPlace'] :
                    self.partner_id.birthplace = getFRDescription(data['birth']['birthPlace'])
            
