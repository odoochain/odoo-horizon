odoo.define('website_booking.browser_mobile', function (require) {
"use strict";

/* global moment, Materialize, $, location, odoo, gapi */

var core = require('web.core');
var ajax = require('web.ajax');
var data = require('web.data');
var session = require('web.session');
var Widget = require('web.Widget');
var Dialog = require("web.Dialog");
var time = require('web.time');
var framework = require('web.framework');

var Model = require("web.Model");

var _t = core._t;
var qweb = core.qweb;

ajax.loadXML('/website_booking/static/src/xml/browser_mobile.xml', qweb);

var BrowserMobile = Widget.extend({
    template: 'website_booking.browser_mobile',
    
    events: {
        "click #today" : function (event) {
            this.date = this.today;
            this.$('#tomorrow').removeClass('red');
            this.$('#today').addClass('red');
        },
        "click #tomorrow" : function (event) {
            this.date = this.tomorrow;
            this.$('#today').removeClass('red');
            this.$('#tomorrow').addClass('red');
        },
        "change #from_hour": function (event) {
            var self = this;
            var fromTime = self.$('#from_hour').timepicker('getTime', this.date.toDate());
            var events = this.schedule.events;
            self.$('#from_hour').removeClass('invalid');
            self.$('#from_hour').addClass('valid');
            for (event in events) {
                if (moment(events[event].start).isBefore(fromTime) && moment(events[event].end).isAfter(fromTime)){
                    self.$('#from_hour').removeClass('valid');
                    self.$('#from_hour').addClass('invalid');
                    break;
                } 
            }
            self.updateRoomList();
            self.updateSendButton();
        },
        "change #to_hour": function (event) {
            var self = this;
            var fromTime = self.$('#from_hour').timepicker('getTime', this.date.toDate());
            var toTime = self.$('#to_hour').timepicker('getTime', this.date.toDate());
            var events = this.schedule.events;
            self.$('#to_hour').removeClass('invalid');
            self.$('#to_hour').addClass('valid');
            for (event in events) {
                if (moment(events[event].start).isBefore(toTime) && moment(events[event].end).isAfter(toTime)){
                    self.$('#to_hour').removeClass('valid');
                    self.$('#to_hour').addClass('invalid');
                    break;
                } 
            }
            if(!self.user.in_group_14 && !self.user.in_group_15) {
                if((fromTime.getHours() + fromTime.getMinutes()/60) > (toTime.getHours() + toTime.getMinutes()/60 - 0.5)) {
                    self.$('#to_hour').removeClass('valid');
                    self.$('#to_hour').addClass('invalid');
                }
                if((fromTime.getHours() + fromTime.getMinutes()/60) < (toTime.getHours() + toTime.getMinutes()/60 - 2)) {
                    self.$('#to_hour').removeClass('valid');
                    self.$('#to_hour').addClass('invalid');
                }
            } else {
                self.$('#to_hour').removeClass('invalid');
                self.$('#to_hour').addClass('valid');
            }
            self.updateRoomList();
            self.updateSendButton();
        },     
    },
    
    init: function(parent) {
        this._super(parent);
        this.date = this.today = moment(new Date());
        this.tomorrow = moment(new Date()).add(1,'days');
    },
    
    start: function() {
        this._super.apply(this, arguments);
        var self = this;
        self.$('select.select-asset-id').material_select();
        self.$('#from_hour').timepicker({
            'timeFormat': 'H:i',
            'minTime': '8:00',
            'maxTime': '21:30',
        });
        self.$('#from_hour').on('change', function() {
            var newTime = self.$('#from_hour').timepicker('getTime');
            self.$('#to_hour').timepicker('option', 'minTime', newTime);
        });
        self.$('#to_hour').timepicker({
            'timeFormat': 'H:i',
            'minTime': '8:30',
            'maxTime': '22:00',
            'showDuration': true,
        });
        
        Materialize.updateTextFields();
    },
    
    updateRoomList: function() {
        var self = this;
        var fromTime = self.$('#from_hour').timepicker('getTime');
        var toTime = self.$('#to_hour').timepicker('getTime');
        if (fromTime && toTime) {
            var start = moment(self.date).local().set('hour',fromTime.getHours()).set('minutes',fromTime.getMinutes()).set('seconds',0);
            var stop = moment(self.date).local().set('hour',toTime.getHours()).set('minutes',toTime.getMinutes()).set('seconds',0);
            ajax.jsonRpc('/booking/rooms', 'call', {
        				'start' : time.moment_to_str(start),
        				'end' : time.moment_to_str(stop),
        				'self_id' : self.event ? self.event.id : '',
    	    	}).done(function(rooms){
                var roomSelect = self.$('select.select-asset-id').empty().html(' ');
                for(var room_idx in rooms) {
                    var room = rooms[room_idx];
                    // add new value
                    roomSelect.append(
                      $("<option></option>")
                        .attr("value",room.id)
                        .text(room.name)
                    );
                }
                roomSelect.removeAttr( "disabled" )
        	    roomSelect.material_select();
        	    Materialize.updateTextFields();
        	    self.updateSendButton();
        	});
        }
    },
    
    updateSendButton: function() {
        if(this.$('.invalid').length > 0) {
            this.$('.request-booking').attr( 'disabled', '' );
        } else {
            this.$('.request-booking').removeAttr( 'disabled' );
        }
    },
    
});

core.action_registry.add('website_booking.browser_mobile', BrowserMobile);

return BrowserMobile;

});