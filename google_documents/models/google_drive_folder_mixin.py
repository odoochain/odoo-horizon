# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2022 ito-invest.lu
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
import json
import requests

from datetime import date, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import google.oauth2.credentials
import google_auth_oauthlib.flow

_logger = logging.getLogger(__name__)

class GoogleDriveFolderMixin(models.AbstractModel):
    _name = "google_drive_folder.mixin"
    
    google_drive_folder_id = fields.Char(string="Google Drive Folder Id",copy=False)
    
    def _compute_google_drive_connected(self):
        self.google_drive_connected = self.env.company.google_drive_id and self.env.company.google_drive_id.is_google_drive_connected()
        
    google_drive_connected = fields.Boolean(string="Is Google Drive Connected", compute=_compute_google_drive_connected)

    def _compute_google_drive_files(self):
        google_service = self.env['google.service']
        for rec in self:
            try :
                if google_service.is_google_drive_connected() and rec.google_drive_folder_id :
                    google_service.get_files_from_folder_id(rec.google_drive_folder_id)
            except:
                pass
        
            gdf_id = self.env['google_drive_file'].create({
                'name' : 'test_file.txt',
                'description' : 'Fichier Test',
                'url' : 'https://test.com/test_files.txt',
                'mimetype' : 'text/plain'
            })

            rec.google_drive_files = [[6,_,gdf_id.ids]]

    google_drive_files = fields.Many2many('google_drive_file',string="Google Drive Files", compute=_compute_google_drive_files)

    def action_authorize_google_drive(self):
        google_service = self.env['google.service']
        return google_service._get_authorize_uri('https://horizon.student-crlg.be','drive','https://www.googleapis.com/auth/drive.readonly')

class GoogleDriveFile(models.TransientModel):
    _name = "google_drive_file"
    
    name = fields.Char('Name')
    description = fields.Text('Description')
    url = fields.Char('Url')
    mimetype = fields.Char('Mime Type', readonly=True)
    
class Company(models.Model):
    _inherit = 'res.company'
    
    google_drive_id = fields.Many2one('google.drive.service', 'Google Drive Service')
    
class GoogleDriveService(models.Model):
    _name = 'google.drive.service'
    
    name = fields.Char('name')
    
    drive_auth_code = fields.Char('Drive Auth Code')
    drive_client_config_json = fields.Text('Drive Client Config JSON')
    drive_credentials_json = fields.Text('Drive Access Credentials')
    
    def action_connect_to_drive(self):
        self.ensure_one()
        # Use the client_secret.json file to identify the application requesting
        # authorization. The client ID (from that file) and access scopes are required.
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=json.loads(self.drive_client_config_json),
            scopes=self._get_drive_scope())
        
        # Indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required. The value must exactly
        # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
        # configured in the API Console. If this value doesn't match an authorized URI,
        # you will get a 'redirect_uri_mismatch' error.
        flow.redirect_uri = self._get_redirect_uri()
        
        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            prompt='consent',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true',
            state=self.id)
        
        return {
              'type'     : 'ir.actions.act_url',
              'url'      : authorization_url,
              'target'   : 'self'
        }
        
    def action_refresh_token(self):
        self.ensure_one()
        if not self.drive_credentials_json :
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config=json.loads(self.drive_client_config_json),
                scopes=self._get_drive_scope())
            
            flow.redirect_uri = self._get_redirect_uri()

            log = logging.getLogger()
            
            log.setLevel(logging.DEBUG)
            
            flow.fetch_token(code=self.drive_auth_code)
            
            log.setLevel(logging.INFO)
            
            credentials = flow.credentials
            cred = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            self.drive_credentials_json = json.dumps(cred)
        else :
            cred = self._json_to_cred(self.drive_credentials_json)
            cred.refresh(None)
            self.drive_credentials_json = json.dumps(cred.to_json())
        

    def is_google_drive_connected(self):
        self.ensure_one()
        if not self.drive_auth_code:
            raise UserError('Google Drive Not Connected - please contact your administrator.')
        
        if not self.drive_refresh_token :
            self.action_refresh_token()
        elif self.drive_token_validity and self.drive_token_validity >= (fields.Datetime.now() + timedelta(minutes=1)) :
            self.action_refresh_token()
        
        _logger.info(self.drive_access_token)
        _logger.info(self.drive_refresh_token)
        _logger.info(self.drive_ttl)
        return self.drive_access_token
    
    def get_files_from_folder_id(self, folderId):
            status, response, ask_time = self._do_request('/drive/v3/files',{
                'q' : '%s in parents' % folderId,
            })
            _logger.info(status)
            _logger.info(response)
            _logger.info(ask_time)
            
    def _get_drive_scope(self):
        return ['https://www.googleapis.com/auth/drive.readonly']
        
    def _get_redirect_uri(self):
        return '%s/google_documents/authorize' % self.env.user.get_base_url()