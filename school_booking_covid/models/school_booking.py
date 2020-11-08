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

from openerp import api, fields, models, _, tools
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

def to_tz(datetime, tz):
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

class Event(models.Model):
    """ Model for School Event """
    _inherit = 'calendar.event'
    
    @api.multi
    def confirm(self):
        self.write({'state': 'open'})
        
    @api.multi
    def to_draft(self):
        self.write({'state': 'draft'})
        
    @api.one
    @api.constrains('state')
    def _change_name_from_state(self):
        if self.state == 'draft':
            name = self.name
            if name.find('[') != -1:
                name = name[:-5]
            self.name = '%s [NC] ' % name
        elif self.state == 'open':
            name = self.name
            if name.find('[') != -1:
                name = name[:-5]
            self.name = '%s [OK] ' % name
            
            cr = self.env.cr
            uid = self.env.uid
            context = self.env.context
        
            mail_to_ids = self.attendee_ids.mapped('id')
                
            if mail_to_ids:
                current_user = self.pool['res.users'].browse(cr, uid, uid, context=context)
                if self.pool['calendar.attendee']._send_mail_to_attendees(cr, uid, mail_to_ids, template_xmlid='calendar_template_meeting_confirmation', email_from=current_user.email, context=context):
                    self.pool['calendar.event'].message_post(cr, uid, self.id, body=_("A email has been send to specify that the booking is confirmed !"), subtype="calendar.subtype_invitation", context=context)

    @api.one
    @api.constrains('room_id')
    def _check_room_quota(self):
        
        _logger.info('Check constraints _check_room_quota on record %s using COVID rules' % self.id)
        if self.room_id :
        
            # Admin is king
            
            if self.env.uid == 1 :
                return
    
            # Get user timezone
            
            utc_tz = pytz.UTC
            #user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'Europe/Brussels')
            user_tz = pytz.timezone('Europe/Brussels')
    
            # Prevent concurrent bookings

            domain = [('room_id','=',self.room_id.id), ('start', '<', self.stop_datetime), ('stop', '>', self.start_datetime)]
            conflicts_count = self.env['calendar.event'].sudo().with_context({'virtual_id': True}).search_count(domain)
            if conflicts_count > 1:
                raise ValidationError(_("Concurrent event detected - %s in %s") % (self.start_datetime, self.room_id.name))
    
            # Constraint not for employees and teatchers
    
            if self.env.user.has_group('school_management.group_employee'):
                return
    
            if self.env.user.has_group('school_management.group_teacher'):
                return
    
            # Constraint on student events
            
            student_event = self.env['ir.model.data'].xmlid_to_object('school_booking.school_student_event_type')
            
            if student_event in self.categ_ids:
                
                dt = to_tz(fields.Datetime.from_string(self.start_datetime),utc_tz)
                
                if dt.minute != 0 and dt.minute != 30 :
                    raise ValidationError(_("Invalid booking, please use standard booking."))
                
                now = to_tz(datetime.now(),user_tz)
                
                start_time = fields.Datetime.from_string(self.start_datetime)
               
                next_day = now + timedelta(days= 7-now.weekday() if now.weekday()>3 else 1)
                
                last_booking_day = now - timedelta(days=now.weekday()) + timedelta(days=6) # end of week
                
                if now.weekday > 3 :
                    last_booking_day = last_booking_day + timedelta(days=7) # end of next week
                
                if start_time.day <= next_day.day :
                    raise ValidationError(_("You must make your booking two days in advance."))
                
                if start_time.day > last_booking_day.day :
                    raise ValidationError(_("Bookings are not yet open for this date."))
                
                if dt < (datetime.now() + timedelta(minutes=-30)):
                    raise ValidationError(_("You cannot book in the past."))
                
                event_day = fields.Datetime.from_string(self.start_datetime).date()
                
                duration_list = self.env['calendar.event'].read_group([
                        ('user_id', '=', self.user_id.id), ('room_id','!=',False), ('categ_ids','in',student_event.id), ('start', '>=', fields.Datetime.to_string(event_day)), ('start', '<=', fields.Datetime.to_string(event_day + timedelta(days=1)))
                    ],['room_id','duration'],['room_id'])
                for duration in duration_list:
                    if duration['duration'] and duration['duration'] > 2:
                        raise ValidationError(_("You cannot book the room %s more than two hours per day") % (duration.get('room_id','')[1]))
                
                duration_list = self.env['calendar.event'].read_group([
                        ('user_id', '=', self.user_id.id), ('categ_ids','in',student_event.id), ('room_id','!=',False), ('start', '>=', fields.Datetime.to_string(event_day)), ('start', '<=', fields.Datetime.to_string(event_day + timedelta(days=1)))
                    ],['start_datetime','duration'],['start_datetime:day'])
                for duration in duration_list:
                    if duration['duration'] and duration['duration'] > 6:
                        raise ValidationError(_("You cannot book more than six hours per day - %s") % duration['start_datetime:day'])
                
                duration_list = self.env['calendar.event'].read_group([
                        ('user_id', '=', self.user_id.id), ('start', '>', fields.Datetime.now()), ('room_id','!=',False), ('categ_ids','in',student_event.id), ('start', '>=', fields.Datetime.to_string(event_day)), ('start', '<=', fields.Datetime.to_string(event_day + timedelta(days=1)))
                    ],['start_datetime','duration'],['start_datetime:day'])
                for duration in duration_list:
                    if duration['duration'] > 4:
                        raise ValidationError(_("You cannot book more than four hours in advance per day - %s") % duration['start_datetime:day'])
                        
                _logger.info('Check done')
                    
            
