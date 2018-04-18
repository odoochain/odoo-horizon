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

var EventList = Widget.extend({
    template: 'website_booking.browser_mobile_event_list',
    
    init: function(parent, options) {
        this.calEvents = options.calEvents;
    },
    
});

var BrowserWidget = Widget.extend({
    
    events: {
        "click #today" : function (event) {
            if(this.date != this.today) {
                this.date = this.today;
                this.$('#tomorrow').removeClass('blue');
                this.$('#today').addClass('blue');
                this.clearAll();
            }
        },
        "click #tomorrow" : function (event) {
            if(this.date != this.tomorrow) {
                this.date = this.tomorrow;
                this.$('#today').removeClass('blue');
                this.$('#tomorrow').addClass('blue');
                this.clearAll();
            }
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
        self.$('#today').addClass('blue');
    },
    
});

var BrowserEditor = BrowserWidget.extend({
    template: 'website_booking.browser_mobile_editor',
    
    events: {
        "change #from_hour": function (event) {
            var self = this;
            var fromTime = self.$('#from_hour').timepicker('getTime', this.date.toDate());
            self.$('#from_hour').removeClass('invalid');
            self.$('#from_hour').addClass('valid');
            self.updateRoomList();
            self.updateSendButton();
        },
        "change #to_hour": function (event) {
            var self = this;
            var fromTime = self.$('#from_hour').timepicker('getTime', this.date.toDate());
            var toTime = self.$('#to_hour').timepicker('getTime', this.date.toDate());
            self.$('#to_hour').removeClass('invalid');
            self.$('#to_hour').addClass('valid');
            /*if(!self.user.in_group_14 && !self.user.in_group_15) {
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
            }*/
            self.updateRoomList();
            self.updateSendButton();
        },     
    },
    
    init: function(parent) {
        this._super(parent);
        var self = this;
        self.calEvents = [];
        session.session_bind().then(function(){
            if (session.uid) {
                self.is_logged = true;
                self.uid = session.uid;
                new Model('res.users').call("search_read", 
                    [[["id", "=", session.uid]], ["id","name","in_group_14","in_group_15","in_group_16",]],
                    {context: session.context}).then(function (user_ids) {
                        session.user = user_ids[0];
                        self.user = session.partner;
                });
                new Model('res.partner').call("search_read", 
                    [[["id", "=", session.partner_id]], ["id","name"]],
                    {context: session.context}).then(function (partner_ids) {
                        session.partner = partner_ids[0];
                        self.partner = session.partner;
                });
                ajax.jsonRpc('/booking/my_events', 'call', {
            				'start' : time.moment_to_str(self.today),
            				'end' : time.moment_to_str(self.tomorrow),
        	    	}).done(function(calEvents){
        	    	    
        	    	    calEvents.forEach(function(evt) {
                            var color = '#ff4355';
            	    	    if (evt.categ_ids.includes(9)) {
            	    	        color = '#00bcd4';
            	    	    } else {
            	    	        if(evt.categ_ids.includes(7)) {
            	    	            color = '#2962ff';
            	    	        } else {
            	    	            if(evt.categ_ids.includes(8)) {
                	    	            color = '#e65100';
                	    	        } else {
                	    	            if (session.uid == evt.user_id[0]) {
                	    	                color = '#ffc107';
                	    	            }
                	    	        }
            	    	        }
            	    	    } 
                            self.calEvents.push({
                                'start': moment.utc(evt.start).local(),
                                'end': moment.utc(evt.stop).local(),
                                'title': /*evt.partner_id[1] + " - " +*/ evt.name,
                                'allDay': evt.allday,
                                'id': evt.id,
                                'resourceId':evt.room_id[0],
                                'resourceName':evt.room_id[1],
                                'color': color,
                                'user_id' : evt.user_id[0],
                            });
                        });
                        self.updateEventList();
                    }
                );
            } else {
                ajax.jsonRpc('/booking/login_providers', 'call', {redirect : '/booking#debug'}).done(function(providers){
                    if(providers.length > 0) {
                        var provider = providers[0];
                        var link = provider.auth_link
                        window.location.replace(provider.auth_link);
                    }
                });
            }
        });
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
            this.$('.confirm').attr( 'disabled', '' );
        } else {
            this.$('.confirm').removeAttr( 'disabled' );
        }
    },
    
    updateEventList: function() {
        var event_list = new EventList(this, {'calEvents' : this.calEvents});
        event_list.appendTo(this.$('.mobile_list').empty());
    },
    
    clearAll: function() {
        var self = this;
        self.$('#to_hour').val('');
        self.$('#to_hour').removeClass('valid');
        self.$('#to_hour').addClass('invalid');
        self.$('#from_hour').val('');
        self.$('#from_hour').removeClass('valid');
        self.$('#from_hour').addClass('invalid');
        self.$('select.select-asset-id').val('');
        self.$('select.select-asset-id').removeClass('valid');
        self.$('select.select-asset-id').removeClass('invalid');
        self.$('select.select-asset-id').empty().html(' ');
        self.$('.confirm').attr( 'disabled', '' );
        self.updateEventList();
    },
});

var BrowserSearch = BrowserWidget.extend({
    template: 'website_booking.browser_mobile_search',

    events: {
        "change #search" : function (event) {
            console.log('Search ' +  this.$('#search').val());
        },
    },
    
});

var BrowserMobile = Widget.extend({
    template: 'website_booking.browser_mobile',
    
    events: {
        "click #editor" : function (event) {
            this.switchToEditor();
        },
        
        "click #search" : function (event) {
            this.switchToSearch();
        },
        
        "click #logout" : function (event) {
            var self = this;
            self.is_logged = false;
            self.uid = false;
            self.avatar_src = false;
            self.rpc("/web/session/destroy", {}).always(function(o) {
                    window.open("http://accounts.google.com/logout", "something", "width=550,height=570");
                    location.reload();
            });
        },
    },
    
    renderElement: function() {
        this._super.apply(this, arguments);
        this._current_state = $.deparam(window.location.hash.substring(1));
        this.mode = '';
        this.editor = new BrowserEditor(this);
        this.search = new BrowserSearch(this);
        this.switchToEditor();
    },
    
    switchToEditor: function() {
        var self = this;
        if(this.mode != 'editor') {
            this.mode = 'editor';
            self.editor.appendTo(this.$(".mobile_content").empty());    
        }
    },
    
    switchToSearch: function() {
        var self = this;
        if(this.mode != 'search') {
            this.mode = 'search';
            self.search.appendTo(this.$(".mobile_content").empty());
        }
    },
});

core.action_registry.add('website_booking.browser_mobile', BrowserMobile);

return BrowserMobile;

});