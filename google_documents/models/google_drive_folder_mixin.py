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

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

_logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

class GoogleDriveFolderMixin(models.AbstractModel):
    _name = "google_drive_folder.mixin"
    
    google_drive_folder_id = fields.Char(string="Google Drive Folder Id",copy=False)
    
    def _compute_google_drive_connected(self):
        self.google_drive_connected = self.env.company.google_drive_id and self.env.company.google_drive_id.is_google_drive_connected()
        
    google_drive_connected = fields.Boolean(string="Is Google Drive Connected", compute=_compute_google_drive_connected)

    def action_refresh_google_drive_files(self):
        google_service = self.env.company.google_drive_id
        for rec in self:
            if google_service.is_google_drive_connected() and rec.google_drive_folder_id :
                gdf_ids = google_service.get_files_from_folder_id(rec.google_drive_folder_id)
                rec.google_drive_files = [[6,_,gdf_ids.ids]]
            else :
                rec.google_drive_files = False

    google_drive_files = fields.One2many('google_drive_file', 'res_id', string="Google Drive Files")

class GoogleDriveFile(models.Model):
    _name = "google_drive_file"
    
    res_model = fields.Char('Related Record Model')
    res_id = fields.Many2oneReference('Related Record ID', model_field='res_model')
    
    name = fields.Char('Name')
    url = fields.Char('Url')
    mimeType = fields.Char('Mime Type')
    googe_drive_id = fields.Char('Google Drive Id')
    
    def _auto_init(self):
        res = super(GoogleDriveFile, self)._auto_init()
        tools.create_index(self._cr, 'google_drive_file_res_id_idx',
                           self._table, ['res_model', 'res_id'])
        return res
    
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
            scopes=SCOPES)
        
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
                scopes=None)
            flow.redirect_uri = self._get_redirect_uri()
            
            import logging
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            
            flow.fetch_token(code=self.drive_auth_code)
            
            logger.setLevel(logging.INFO)
            
            self.drive_credentials_json = json.dumps(flow.credentials.to_json())

    def is_google_drive_connected(self):
        self.ensure_one()
        return self.drive_credentials_json
    
    def get_files_from_folder_id(self, folderId):

        drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=self._get_credential())

        all_file_list = []
        folder_queue = [folderId]
        gdf_models = self.env['google_drive_file']
        gdf_ids = self.env['google_drive_file']
        while len(folder_queue) != 0:
            current_folder_id = folder_queue.pop(0)
            file_list = drive.files().list(q=f"'{current_folder_id}' in parents and trashed=false",supportsAllDrives=True,includeItemsFromAllDrives=True,fields='files(id,name,mimeType,webViewLink)').execute()
            for file1 in file_list['files']:
                if file1['mimeType'] == 'application/vnd.google-apps.folder':
                    folder_queue.append(file1['id'])
                else :
                    all_file_list.append({
                        'name' : file1['name'],
                        'googe_drive_id' : file1['id'],
                        'mimeType' : file1['mimeType'],
                        'url' : file1['webViewLink']
                    })
        return gdf_models.create(all_file_list)
        
    def _get_redirect_uri(self):
        return '%s/google_documents/authorize' % self.env.user.get_base_url()
        
    def _get_credential(self):
        credential_json = json.loads(self.drive_credentials_json)
        if credential_json is None:
            return None
        credential = google.oauth2.credentials.Credentials.from_authorized_user_info(credential_json)
        return credential