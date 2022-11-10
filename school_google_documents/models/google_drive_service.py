import logging

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class google_drive_folder_mixin(models.AbstractModel):
    _name = "school.google_drive_folder.mixin"
    
    google_drive_folder_id = fields.Char(string="Google Drive Folder Id",copy=False)

    google_drive_files = fields.Many2many(string="Google Drive Files", compute=_compute_google_drive_files)

    def _compute_google_drive_files(self):
        gdf_id = self.env['school.google_drive_file'].create({
            'name' : 'test_file.txt',
            'description' : 'Fichier Test',
            'url' : 'https://test.com/test_files.txt',
            'mimetype' : 'text/plain'
        })
        for rec in self:
            self.google_drive_files = [[4,_,gdf_id]]

class GoogleDriveFile(models.TransientModel):
    _name = "school.google_drive_file"
    
    name = fields.Char('Name')
    description = fields.Text('Description')
    
    type = fields.Selection([('url', 'URL')],string='Type', required=True, default='url',help="All the time URL in this case.")
    url = fields.Char('Url')
    
    mimetype = fields.Char('Mime Type', readonly=True)
    
class GoogleDriceService(models.Model):
    _name = 'google.drive.sync'
    _description = "Synchronize a Google Drive folder with a record"
    
    