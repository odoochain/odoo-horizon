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
import traceback

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class ResUser(models.Model):
    _inherit = 'res.users'

    national_id = fields.Char(string='National ID')

class Partner(models.Model):
    _inherit = 'res.partner'

    inscription_ids = fields.One2many('school.bced.inscription', 'partner_id', string='BCED Inscriptions', ondelete='restrict')
    inscription_count = fields.Integer(compute='_compute_inscription_count', string='BCED Inscription Count')

    @api.depends('inscription_ids')
    def _compute_inscription_count(self):
        for rec in self :
            rec.inscription_count = len(rec.inscription_ids)

    def action_update_bced_personne(self):
        for rec in self :
            if rec.inscription_id :
                try :
                    # TODO : update contact information from BCED Web Service
                    rec.inscription_id.action_update_partner_information()
                except Exception as e :
                    _logger.error('Error while updating contact information : %s', e)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': _('Error while updating contact information : %s' % traceback.format_exc()),
                            'next': {'type': 'ir.actions.act_window_close'},
                            'sticky': False,
                            'type': 'warning',
                        }
                    }