# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2023 ito-invest.lu
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
import logging.config
import base64
import os
import io
from datetime import datetime, timedelta
import uuid
from lxml import etree

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class BCEDInscription(models.Model):
    _name = 'school.bced.inscription'
    _description = 'BCED Inscription'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    reference = fields.Char(string='Reference')
    legal_context = fields.Char(string='Legal Context', required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def action_submit(self):
        ws = self.env['school.webservice'].search([('name', '=', 'bced_inscription')], limit=1)
        for rec in self:
            res = ws.publishInscription(rec)
            if res:
                rec.reference = res['inscriptionReference']
            
    def action_revoke(self):
        for rec in self:
            # TODO : implement revoke
            pass
