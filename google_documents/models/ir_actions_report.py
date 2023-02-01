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

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'
    
    google_drive_enabled = fields.Boolean(string='Save in Google Drive',
                                    help='If enabled, the report will be saved in Google Drive.')
                                    
    google_drive_patner_field = fields.Char(string='Partner property to save into',
                             help='This field name is the Partner to which the Google Drive Forlder to save to.')

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        
        pdf_content, type = super(IrActionsReport, self)._render_qweb_pdf(report_ref, res_ids, data)
        
        report_sudo = self._get_report(report_ref)
        
        google_service = self.env.company.google_drive_id
        
        if google_service and self.google_drive_enabled :
            for res_id, stream_data in pdf_content.items():
                record = self.env[report_sudo.model].browse(res_id)
                partner_id = record.get(self.google_drive_patner_field)
                if partner_id.google_drive_folder_id :
                    file = google_service.create_file(stream_data, 'application/pdf', partner_id.google_drive_folder_id)
                    google_drive_file = self.env['google_drive_file'].create({
                        'name' : file['name'],
                        'googe_drive_id' : file['id'],
                        'mimeType' : file['mimeType'],
                        'url' : file['webViewLink'],
                        'res_model' : partner_id._name,
                    })
                    partner_id.google_drive_files += google_drive_file
        return pdf_content, type