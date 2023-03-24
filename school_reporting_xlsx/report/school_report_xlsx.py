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

from odoo import api, fields, models, tools, _
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

def flattern_json(d):
    if len(d) == 0:
        return {}
    from collections import deque
    q = deque()
    res = dict()
    for key, val in d.items(): # This loop push the top most keys and values into queue.
        if not isinstance(val, dict):  # If it's not dict
            if isinstance(val, list):  # If it's list then check list values if it contains dict object.
                temp = list()  # Creating temp list for storing the values that we will need which are not dict.
                for v in val:
                    if not isinstance(v, dict):
                        temp.append(v)
                    else:
                        q.append((key, v))  # if it's value is dict type then we push along with parent which is key.
                if len(temp) > 0:
                    res[key] = temp
            else:
                res[key] = val
        else:
            q.append((key, val))
    while q:
        k, v = q.popleft()  # Taking parent and the value out of queue
        for key, val in v.items():
            new_parent = k + "_" + key  # New parent will be old parent_currentval
            if isinstance(val, list):
                temp = list()
                for v in val:
                    if not isinstance(v, dict):
                        temp.append(v)
                    else:
                        q.append((new_parent, v))
                if len(temp) >= 0:
                    res[new_parent] = temp
            elif not isinstance(val, dict):
                res[new_parent] = val
            else:
                q.append((new_parent, val))
    return res

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
        sheet = workbook.add_worksheet("Registrations")
        for i, obj in enumerate(registrations):
            sheet.write(i, 0, obj.name)
            sheet.write(i, 1, obj.email)
            contact_form_data = json.loads(obj.contact_form_data)
            j = 2
            for key, value in contact_form_data.items():
                if type(value) == list:
                    sheet.write(i, j, json.dumps(value, indent=2))
                else:
                    sheet.write(i, j, value)
                j += 1
