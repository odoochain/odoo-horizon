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

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class google_drive_folder_mixin(models.AbstractModel):
    _name = "school.google_drive_folder.mixin"
    
    google_drive_folder_id = fields.Char(string="Google Drive Folder Id",copy=False)

    def _compute_google_drive_files(self):
        
        for rec in self:
            if rec.google_drive_folder_id :
                self.env['google.service'].get_files_from_folder_id(rec.google_drive_folder_id)
        
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
    
    @api.model
    def get_files_from_folder_id(self, folderId):
        status, response, ask_time = self._do_request('/drive/v3/files',{
            'q' : '%s in parents' % folderId,
        })
        _logger.info(status)
        _logger.info(response)
        _logger.info(ask_time)