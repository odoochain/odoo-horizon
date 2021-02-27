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

import pytz
from datetime import datetime, date, time, timedelta

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

def to_tz(datetime, tz):
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

class Event(models.Model):
    """ Model for School Event """
    _inherit = 'calendar.event'
    
    def confirm(self):
        self.write({'state': 'open'})
        
    def to_draft(self):
        self.write({'state': 'draft'})
        
    @api.constrains('state')
    def _change_name_from_state(self):
        for rec in self :
            if not rec.recurrency :
                if rec.state == 'draft':
                    name = rec.name
                    if name.find('[') != -1:
                        name = name[:-5]
                    rec.name = '%s [NC] ' % name
                elif rec.state == 'open':
                    name = rec.name
                    if name.find('[') != -1:
                        name = name[:-5]
                    rec.name = '%s [OK] ' % name
                    
                    cr = self.env.cr
                    uid = self.env.uid
                    context = self.env.context
                
                    mail_to_ids = rec.attendee_ids.mapped('id')
                        
                    if mail_to_ids:
                        current_user = self.env['res.users'].browse(cr, uid, uid, context=context)
                        if self.env['calendar.attendee']._send_mail_to_attendees(cr, uid, mail_to_ids, template_xmlid='calendar_template_meeting_confirmation', email_from=current_user.email, context=context):
                            self.env['calendar.event'].message_post(cr, uid, rec.id, body=_("A email has been send to specify that the booking is confirmed !"), subtype="calendar.subtype_invitation", context=context)

    @api.constrains('room_id')
    def _check_room_quota(self):
        for rec in self :
            _logger.info('Check constraints _check_room_quota on record %s using COVID rules' % self.id)
            if rec.room_id :
            
                # Admin is king
                
                if self.env.uid == 1 :
                    return
                
                if rec.recurrency :
                    return
                
                # Get user timezone
                
                utc_tz = pytz.UTC
                #user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'Europe/Brussels')
                user_tz = pytz.timezone('Europe/Brussels')
        
                # Prevent concurrent bookings
    
                domain = [('room_id','=',rec.room_id.id), ('start', '<', rec.stop_datetime), ('stop', '>', rec.start_datetime)]
                conflicts_count = self.env['calendar.event'].sudo().with_context({'virtual_id': True}).search_count(domain)
                if conflicts_count > 1:
                    raise ValidationError(_("Concurrent event detected - %s in %s") % (rec.start_datetime, rec.room_id.name))
        
                # Constraint not for employees and teatchers
        
                if self.env.user.has_group('school_management.group_employee'):
                    return
        
                if self.env.user.has_group('school_management.group_teacher'):
                    return
        
                # Constraint on student events
                
                student_event = self.env['ir.model.data'].xmlid_to_object('school_booking.school_student_event_type')
                
                if student_event in rec.categ_ids:
                    
                    dt = to_tz(fields.Datetime.from_string(rec.start_datetime),utc_tz)
                    
                    if dt.minute != 0 and dt.minute != 30 :
                        raise ValidationError(_("Invalid booking, please use standard booking."))
                        
                    now = to_tz(datetime.now(),user_tz)
                    
                    start_time = fields.Datetime.from_string(rec.start_datetime)
                   
                    next_day = now + timedelta(days= 7-now.weekday() if now.weekday()>3 else 1)
                    
                    last_booking_day = now - timedelta(days=now.weekday()) + timedelta(days=6) # end of week
                    
                    _logger.info('check at %s : %s < %s < %s' % (now, next_day, start_time, last_booking_day))
                    
                    if now.weekday > 3 :
                        last_booking_day = last_booking_day + timedelta(days=7) # end of next week
                    
                    if start_time <= next_day :
                        raise ValidationError(_("You must make your booking two days in advance."))
                    
                    if start_time > last_booking_day :
                        raise ValidationError(_("Bookings are not yet open for this date."))
                    
                    if dt < (datetime.now() + timedelta(minutes=-30)):
                        raise ValidationError(_("You cannot book in the past."))
                    
                    event_day = fields.Datetime.from_string(rec.start_datetime).date()
                    
                    duration_list = self.env['calendar.event'].read_group([
                            ('user_id', '=', rec.user_id.id), ('room_id','!=',False), ('categ_ids','in',student_event.id), ('start', '>=', fields.Datetime.to_string(event_day)), ('start', '<=', fields.Datetime.to_string(event_day + timedelta(days=1)))
                        ],['room_id','duration'],['room_id'])
                    for duration in duration_list:
                        if duration['duration'] and duration['duration'] > 3:
                            raise ValidationError(_("You cannot book the room %s more than three hours") % (duration.get('room_id','')[1]))
                    
                    duration_list = self.env['calendar.event'].read_group([
                            ('user_id', '=', rec.user_id.id), ('categ_ids','in',student_event.id), ('room_id','!=',False), ('start', '>=', fields.Datetime.to_string(event_day)), ('start', '<=', fields.Datetime.to_string(event_day + timedelta(days=1)))
                        ],['start_datetime','duration'],['start_datetime:day'])
                    for duration in duration_list:
                        if duration['duration'] and duration['duration'] > 6:
                            raise ValidationError(_("You cannot book more than six hours per day - %s") % duration['start_datetime:day'])
                    
                    _logger.info('Check done')
                        
            
