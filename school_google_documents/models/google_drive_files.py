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

class GoogleDriveFile(models.TransientModel):
    _name = "school.google_drive_file"
    
    name = fields.Char('Name')
    description = fields.Text('Description')
    
    type = fields.Selection([('url', 'URL')],string='Type', required=True, default='url',help="All the time URL in this case.")
    url = fields.Char('Url')
    
    mimetype = fields.Char('Mime Type', readonly=True)
    
class GoogleService(models.AbstractModel):
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
                'drive',
                redirect_uri=f'{base_url}/google_account/authentication'
            )
            
            self.drive_token_validity = fields.Datetime.now() + timedelta(seconds=self.drive_ttl) if self.drive_ttl else False
        
            _logger.info(self.drive_access_token)
            _logger.info(self.drive_refresh_token)
            _logger.info(self.drive_ttl)
            
        elif self.drive_token_validity and self.drive_token_validity >= (fields.Datetime.now() + timedelta(minutes=1)) :
            self._refresh_google_drive_token()
        
        return self.drive_access_token

    @api.model 
    def _refresh_google_drive_token(self):
        # LUL TODO similar code exists in google_drive. Should be factorized in google_account
        get_param = self.env['ir.config_parameter'].sudo().get_param
        client_id = get_param('google_drive_client_id')
        client_secret = get_param('google_drive_client_secret')

        if not client_id or not client_secret:
            raise UserError(_("The account for the Google Drive service is not configured."))

        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            'refresh_token': self.drive_refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
        }

        try:
            _dummy, response, _dummy = self.env['google.service']._do_request(GOOGLE_TOKEN_ENDPOINT, params=data, headers=headers, method='POST', preuri='')
            ttl = response.get('expires_in')
            self.write({
                'drive_access_token': response.get('access_token'),
                'drive_token_validity': fields.Datetime.now() + timedelta(seconds=ttl),
            })
        except requests.HTTPError as error:
            if error.response.status_code in (400, 401):  # invalid grant or invalid client
                # Delete refresh token and make sure it's commited
                self.env.cr.rollback()
                self.write({
                    'drive_access_token': False,
                    'drive_refresh_token': False,
                    'drive_ttl': False,
                    'drive_token_validity': False,
                })
                self.env.cr.commit()
            error_key = error.response.json().get("error", "nc")
            error_msg = _("An error occurred while generating the token. Your authorization code may be invalid or has already expired [%s]. "
                          "You should check your Client ID and secret on the Google APIs plateform or try to stop and restart your drive synchronisation.",
                          error_key)
            raise UserError(error_msg)
    
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
    