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
import time
import werkzeug.utils

from openerp import http
from openerp.http import request

_logger = logging.getLogger(__name__)

class BookingController(http.Controller):

    @http.route('/booking', type='http', auth='public', website=True)
    def booking_browser(self, debug=False, **k):
        return request.render('website_booking.index')

    @http.route('/booking/categories', type='json', auth='public', website=True)
    def booking_categories(self, parent_id=False, debug=False, **k):
        return request.env['school.asset.category'].sudo().search_read([('parent_id', '=', parent_id)],['name','display_name','sequence','parent_id'])

    @http.route('/booking/categories/image/<int:category_id>', type='http', auth='public', website=True)
    def booking_category_image(self, category_id, debug=False, **k):
        category = request.env['school.asset.category'].sudo().browse(category_id)
        if category.image:
            response = werkzeug.wrappers.Response()
            response.mimetype = 'image/png'
            response.headers['Cache-Control'] = 'public, max-age=604800'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
            response.headers['Connection'] = 'close'
            response.headers['Date'] = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime())
            response.headers['Expires'] = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(time.time()+604800*60))
            response.data = category.image.decode('base64')
            return response
        else :
            return werkzeug.exceptions.NotFound('No image found for this category.')
    
    @http.route('/booking/assets', type='json', auth='public', website=True)
    def booking_assets(self, category_id=False, debug=False, **k):
        if category_id:
            return request.env['school.asset'].sudo().search_read([('category_id', '=', category_id)],['name'])
        else:
            return [];
        
    @http.route('/booking/events', type='json', auth='public', website=True)
    def booking_events(self, start, end, timezone=False, category_id=False):
        # TODO : ugply transform
        start = start.replace('T',' ').replace('Z',' ').replace('.000','').strip()
        end = end.replace('T',' ').replace('Z',' ').replace('.000','').strip()
        domain = [
            ('recurrency', '=', 0),
            ('start', '>=', start),    
            ('stop', '<=', end),
            ('asset_id.category_id', '=', category_id),
        ]
        ret = request.env['calendar.event'].sudo().search_read(domain,['name','start','stop','allday','asset_id','partner_id'])
        domain_rec = [
            ('recurrency', '=', 1),    
            ('asset_id.category_id', '=', category_id),
            #('start_date', '>=', start),
            ('stop', '<=', end),
            #('final_date', '>=', start),
        ]
        ret_rec = request.env['calendar.event'].sudo().with_context({'virtual_id': True}).search_read(domain_rec,['name','start','stop','allday','asset_id','partner_id','final_date'])
        # TODO : Post Filter, ugly but how can we do otherwise
        ret_rec = [rec for rec in ret_rec if rec['start'] >= start]
        return ret + ret_rec
        
    @http.route('/booking/editor', type='http', auth='user', website=True)
    def booking_editor(self, debug=False, **k):
        return request.render('website_booking.editor')