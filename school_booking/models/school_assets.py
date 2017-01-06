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

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class Asset(models.Model):
    '''School Asset'''
    _name = 'school.asset'
    _description = 'School Asset'
    _inherit = ['mail.thread']
    
    responsible_id = fields.Many2one('res.partner', string='Responsible', domain="[('type','=','contact')]", required=True, default=lambda self: self.env.user.partner_id)
    require_validation = fields.Boolean(string="Require validation")
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Photo", attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

class AssetType(models.Model):
    """ Event Type """
    _name = 'school.asset_type'
    _description = 'Asset Type'

    name = fields.Char('Event Type', required=True, translate=True)
    require_validation = fields.Boolean(string="Require validation")
    
    hasResponsible = fields.Boolean(string="Has a responsible")
    
class Booking(models.Model):
    """ Model for Calendar Event """
    _name = 'school.booking'
    _description = "Booking"
    _order = "id desc"
    _inherits = {'calendar.event': "event_id"}
    
    event_id = fields.Many2one('calendar.event', string='Event', ondelete='cascade', required=True, auto_join=True)
    
    asset_id = fields.Many2one('school.asset', string='Asset', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', domain="[('type','=','contact')]", required=True, default=lambda self: self.env.user.partner_id)