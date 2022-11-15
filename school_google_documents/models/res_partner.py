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

from datetime import date, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    '''Partner'''
    _name = 'res.partner'
    _inherit = ['res.partner', 'school.google_drive_folder.mixin']

class Users(models.Model):
    '''Users'''
    _name = 'res.users'
    _inherit = ['res.users']
    
    def _set_auth_tokens(self, access_token, refresh_token, ttl):
        google_service = self.env['google.service']
        google_service.drive_access_token = access_token
        google_service.drive_refresh_token = refresh_token
        google_service.drive_ttl = ttl
        google_service.drive_token_validity = fields.Datetime.now() + timedelta(seconds=ttl) if ttl else False