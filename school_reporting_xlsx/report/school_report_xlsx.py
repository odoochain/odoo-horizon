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

import pandas as pd
import numpy as np

from odoo import api, fields, models, tools, _
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

def remove_url_keys(json_data):
    """
    Recursively remove all "url" keys from a nested JSON file.
    :param json_data: JSON data to process.
    :return: Processed JSON data with all "url" keys removed.
    """
    if isinstance(json_data, dict):
        return {k: remove_url_keys(v) for k, v in json_data.items() if k != 'url'}
    elif isinstance(json_data, list):
        return [remove_url_keys(item) for item in json_data]
    else:
        return json_data

class PartnerExportXlsx(models.AbstractModel):
    _name = "report.school_reporting_xlsx.partner_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"
    
    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Partners")
        for i, obj in enumerate(partners):
            bold = workbook.add_format({"bold": True})
            sheet.write(i, 0, obj.name, bold)
            sheet.write(i, 1, obj.email, bold)
            
class RegistrationExportXlsx(models.AbstractModel):
    _name = "report.school_reporting_xlsx.registration_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"
    
    def generate_xlsx_report(self, workbook, data, registrations):
        items = []
        for i, obj in enumerate(registrations):
            item = {
                'id' : obj.id,
                'name' : obj.name,
                'email' : obj.email,
                'contact_form_id' : obj.contact_form_id.id,
                'registration_form_id' : obj.registration_form_id.id,
                'state' : obj.state,
                'kanban_state' : obj.kanban_state
            }
            if obj.contact_form_data :
                contact_form_data = json.loads(obj.contact_form_data)
                contact_form_data = remove_url_keys(contact_form_data)
                item['contact_form_data'] = contact_form_data
            if obj.registration_form_data :
                registration_form_data = json.loads(obj.registration_form_data)
                registration_form_data = remove_url_keys(registration_form_data)
                item['registration_form_data'] = registration_form_data
            items.append(item)
        df = pd.json_normalize(items)
        df = df.fillna('').replace([np.inf, -np.inf], '')
        worksheet = workbook.add_worksheet('Registration')
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        for row_num, row_data in enumerate(df.values):
            for col_num, col_data in enumerate(row_data):
                if isinstance(col_data, list):
                    worksheet.write(row_num + 1, col_num, json.dumps(col_data, indent=2))
                else : 
                    worksheet.write(row_num + 1, col_num, col_data)