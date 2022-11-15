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
import json
import requests

from datetime import date, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo.addons.google_account.models.google_service import GOOGLE_TOKEN_ENDPOINT

_logger = logging.getLogger(__name__)

class google_drive_folder_mixin(models.AbstractModel):
    _name = "school.google_drive_folder.mixin"
    
    google_drive_folder_id = fields.Char(string="Google Drive Folder Id",copy=False)
    
    def _compute_google_drive_connected(self):
        if self.google_drive_folder_id :
            self.google_drive_connected = self.env['google.service'].is_google_drive_connected()
        else :
            self.google_drive_connected = False
        
    google_drive_connected = fields.Boolean(string="Is Google Drive Connected", compute=_compute_google_drive_connected)

    def _compute_google_drive_files(self):
        google_service = self.env['google.service']
        for rec in self:
            try :
                if google_service.is_google_drive_connected() and rec.google_drive_folder_id :
                    google_service.get_files_from_folder_id(rec.google_drive_folder_id)
            except:
                pass
        
            gdf_id = self.env['school.google_drive_file'].create({
                'name' : 'test_file.txt',
                'description' : 'Fichier Test',
                'url' : 'https://test.com/test_files.txt',
                'mimetype' : 'text/plain'
            })

            rec.google_drive_files = [[6,_,gdf_id.ids]]

    google_drive_files = fields.Many2many('school.google_drive_file',string="Google Drive Files", compute=_compute_google_drive_files)

    def action_authorize_google_drive(self):
        google_service = self.env['google.service']
        return google_service._get_authorize_uri('https://horizon.student-crlg.be','drive','https://www.googleapis.com/auth/drive.readonly')

class GoogleDriveFile(models.TransientModel):
    _name = "school.google_drive_file"
    
    name = fields.Char('Name')
    description = fields.Text('Description')
    url = fields.Char('Url')
    mimetype = fields.Char('Mime Type', readonly=True)
    
class Company(models.Model):
    name = 'res.company'
    _inherit = 'res.company'
    
    google_drive_id = fields.Many2one('school.google.service', copy=False)
    
class GoogleService(models.Model):
    name = 'school.google.service'
    _inherit='google.service'
    
    drive_access_token = fields.Char('Drive Access Token', copy=False)
    drive_refresh_token = fields.Char('Drive Refresh Token', copy=False)
    drive_ttl = fields.Float('Drive Token TTL', copy=False)
    drive_token_validity = fields.Datetime('Token Validity', copy=False)
    
    @api.model
    def is_google_drive_connected(self):
        
        if not self.drive_refresh_token :
            base_url = self.env.user.get_base_url()
            self.drive_access_token,  self.drive_refresh_token,  self.drive_ttl = self._get_google_tokens(
                self.env['ir.config_parameter'].sudo().get_param('google_drive_auth_code'),
                'drive'
                )
            
            self.drive_token_validity = fields.Datetime.now() + timedelta(seconds=self.drive_ttl) if self.drive_ttl else False
        
            _logger.info(self.drive_access_token)
            _logger.info(self.drive_refresh_token)
            _logger.info(self.drive_ttl)
            
        elif self.drive_token_validity and self.drive_token_validity >= (fields.Datetime.now() + timedelta(minutes=1)) :
            self.generate_refresh_token('drive', self.drive_access_token)
            
        return self.drive_access_token
    
    @api.model
    def get_files_from_folder_id(self, folderId):
            status, response, ask_time = self._do_request('/drive/v3/files',{
                'q' : '%s in parents' % folderId,
            })
            _logger.info(status)
            _logger.info(response)
            _logger.info(ask_time)
        
    
    @api.model
    def _get_drive_scope(self):
        return 'https://www.googleapis.com/auth/drive.readonly'
    