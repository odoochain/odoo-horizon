odoo.define('website_booking.browser', function (require) {
"use strict";

/* global moment, time */

var core = require('web.core');
var ajax = require('web.ajax');
var Widget = require('web.Widget');
var Dialog = require("web.Dialog");

var Model = require("web.Model");

var _t = core._t;
var qweb = core.qweb;

ajax.loadXML('/website_booking/static/src/xml/browser.xml', qweb);

/**
 * Converts a Moment javascript object to a string using OpenERP's
 * datetime string format (exemple: '2011-12-01 15:12:35').
 * 
 * The time zone of the Date object is assumed to be the one of the
 * browser and it will be converted to UTC (standard for OpenERP 6.1).
 * 
 * @param {Date} obj
 * @returns {String} A string representing a datetime.
 */
function moment_to_str (obj) {
    if (!obj) {
        return false;
    }
    if(obj instanceof Date){
        return time.datetime_to_str(obj);
    }
    return obj.format('YYYY-MM-DD hh:mm:ss');
}

var CalendarWidget = Widget.extend({
    template: 'website_booking.browser_calendar',
    
    get_fc_init_options: function() {
        return {
            header: {
    			left: 'prev,next today',
    			center: 'title',
    			right:'',
    		},
    		locale: moment.locale,
    		timezone: "UTC",
    		editable: false,
    		height: 720,
    		locale: 'fr',
    		titleFormat: 'dddd, D MMMM',
    		defaultDate: moment(),
    		defaultView: 'agendaDay',
    		minTime: "07:00:00",
    		maxTime: "20:00:00",
    		navLinks: true, // can click day/week names to navigate views
    		eventLimit: true, // allow "more" link when too many events
    		refetchResourcesOnNavigate : false,
    		timezone : 'locale',
        }
    },
    
    renderElement: function() {
        this._super.apply(this, arguments);
        var self = this;
        self.$calendar = this.$el;
        self.$calendar.fullCalendar(
		    self.get_fc_init_options()
		);
    },
    
    start : function() {
        this._super.apply(this, arguments);
        var self = this;
        // Force a refresh to get it right
        setTimeout(function() {
            self.$calendar.fullCalendar('changeView');
            self.$('.fc-button').removeClass('fc-button fc-state-default fc-corner-left fc-corner-right').addClass('waves-effect waves-light btn');
        }, 100);
    },
    
    refetch_events: function() {
        this.$calendar.fullCalendar('refetchEvents');
    },
     
});

var Schedule =  CalendarWidget.extend({

    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.date = parent.date;
        this.asset_id = false;
    },

    get_fc_init_options: function() {
        var self = this;
        return $.extend(this._super(),{
            header: {
                left: '',
    			center: '',
    			right:'',
    		},
            defaultDate: this.date,
            height: 640,
            events: self.fetch_events.bind(this),
            allDaySlot: false,
            dayClick: self.day_click.bind(this),
        });
    },
    
    day_click : function(date, jsEvent, view) {
        this.trigger_up('click_scheduler', {'date' : date, 'jsEvent' : jsEvent, 'view' : view});
    },
    
    fetch_events: function(start, end, timezone, callback) {
        var self = this;
        if(self.asset_id) {
            self.events = [];
            ajax.jsonRpc('/booking/events', 'call', {
    	    		'asset_id':this.asset_id,
    				'start' : moment(start).format('YYYY-MM-DD HH:mm:ss'),
    				'end' : moment(end).format('YYYY-MM-DD HH:mm:ss'),
    	    	}).done(function(events){
                    events.forEach(function(evt) {
                        self.events.push({
                            'start': moment(evt.start).format('YYYY-MM-DD HH:mm:ss'),
                            'end': moment(evt.stop).format('YYYY-MM-DD HH:mm:ss'),
                            'title': /*evt.partner_id[1] + " - " +*/ evt.name,
                            'allDay': evt.allday,
                            'id': evt.id,
                            'resourceId':evt.room_id[0],
                            'color': '#FA8FB1',
                        });
                    });
                    //console.log([start, end, events])
                    callback(self.events);
                }
            );
        }
    },
    
    set_asset_id: function(asset_id) {
        this.asset_id = asset_id;
        this.refetch_events();
    },
    
});

var NewBookingDialog = Widget.extend({
    template: 'website_booking.new_booking_dialog',
    
    events: {
        "click .request-booking": function (event) {
            var self = this;
            var fromTime = self.$('#from_hour').timepicker('getTime');
            var toTime = self.$('#to_hour').timepicker('getTime');
            var start = moment(self.date).set('hour',fromTime.getHours()).set('minutes',fromTime.getMinutes()).set('seconds',0);
            var stop = moment(self.date).set('hour',toTime.getHours()).set('minutes',toTime.getMinutes()).set('seconds',0);
            
            new Model('calendar.event').call('create', [{
                'name' : self.$('#textarea1').val(),
                'start': start.format('YYYY-MM-DD HH:mm:ss'),
                'stop': stop.format('YYYY-MM-DD HH:mm:ss'),
                'room_id': parseInt(self.$( "select.select-asset-id" ).val()),
            }]).then(function (id) {
                self.trigger_up('newEvent', {'id': id});
            });
        },
        "change .select-asset-id": function (event) {
            this.schedule.set_asset_id(parseInt(this.$( "select.select-asset-id" ).val()));
        },
    },
    
    custom_events: {
        'click_scheduler' : 'click_scheduler',
    },
    
    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.ressources = parent.cal.ressources;
        this.date = parent.cal.$calendar.fullCalendar( 'getDate' );
    },

    renderElement: function() {
        this._super.apply(this, arguments);
        var self = this;
        // Fill navigation panel
        self.schedule = new Schedule(this);
        self.schedule.appendTo(this.$(".schedule"));
    },

    start: function() {
        this._super.apply(this, arguments);
        var self = this;
        self.$('select').material_select();
        self.$('#from_hour').timepicker({
            'timeFormat': 'H:i',
        });
        self.$('#from_hour').on('change', function() {
            var newTime = self.$('#from_hour').timepicker('getTime');
            if (newTime) { // Not null
                self.$('#to_hour').timepicker('option', 'minTime', newTime);
            }
        });
        self.$('#to_hour').timepicker({
            'timeFormat': 'H:i',
            'showDuration': true,
        });
    },

    click_scheduler: function(event) {
        var requested_date = event.data.date;
        
        this.$('#from_hour').timepicker('setTime', requested_date.format("HH:mm"));
        this.$('#to_hour').timepicker('option', 'minTime', requested_date.format("HH:mm"));
        requested_date.add(1, 'hours');
        this.$('#to_hour').timepicker('setTime', requested_date.format("HH:mm"));
        Materialize.updateTextFields();
    },
    
});

var NavigationCard = Widget.extend({
    template: 'website_booking.browser_navigation_card',
    
    events: {
        "click .navbar-card": function (event) {
            event.preventDefault();
            var self = this;
            self.getParent().$('.navbar-card.active').removeClass('active');
            self.$(event.currentTarget).addClass('active');
            var category_id = self.$(event.currentTarget).data('category-id');
            if(self.to_parent) {
                self.trigger_up('up_category', {'category' : self.category});
            } else {
                self.trigger_up('click_category', {'category' : self.category});
            }
        },
    },
    
    init: function(parent, category, to_parent) {
        this._super(parent);
        this.category = category;
        this.to_parent = to_parent;
    },
    
    set_active: function() {
        this.getParent().$el.find('.z-depth-5').removeClass('z-depth-5')
        this.$el.find('.navbar-card').addClass('z-depth-5');
    },
    
});

var Navigation = Widget.extend({
    template: 'website_booking.browser_navigation',
    
    custom_events: {
        'click_category' : 'click_category',
        'up_category' : 'up_category',
    },
    
    renderElement: function() {
        this._super.apply(this, arguments);
        var self = this;
        self.cat_path = [];
        self.parent_category = false;
        ajax.jsonRpc('/booking/categories', 'call', {}).done(function(categories){
                self.categories = categories;
                self.set_categories(self.categories,false);
            }
        );
    },
    
    set_categories: function(categories, up_category) {
        var self = this;
        self.$(".categories").empty();
        self.categories.forEach(function(category) {
            var card = new NavigationCard(self, category, false);
            card.appendTo(self.$(".categories"));
        });
        if(up_category) {
            var card = new NavigationCard(self, up_category, true);
            card.appendTo(self.$(".categories"));
        }
    },
    
    click_category : function(event) {
        var self = this;
        var cat = event.data.category;
        ajax.jsonRpc('/booking/categories', 'call', {'parent_id':cat.id}).done(function(categories){
                if(categories.length > 0) {
                    self.cat_path.push(self.parent_category);
                    self.parent_category = cat;
                    self.categories = categories;
                    self.set_categories(self.categories,self.parent_category);
                } else {
                    // We are on a leaf
                    event.target.set_active();
                }
            }
        );
        self.trigger_up('switch_category', {'category' : cat});
    },
    
    up_category : function(event) {
        var self = this;
        self.parent_category = self.cat_path.pop();
        ajax.jsonRpc('/booking/categories', 'call', {'parent_id':self.parent_category ? self.parent_category.id : false}).done(function(categories){
                if(categories.length > 0) {
                    self.categories = categories;
                    self.set_categories(self.categories,self.parent_category);
                }
            }
        );
        self.trigger_up('switch_category', {'category' : self.parent_category});
    },
    
});

var Calendar = CalendarWidget.extend({

    get_fc_init_options: function() {
        var self = this;
        return $.extend(this._super(),{
            events: self.fetch_events.bind(this),
    		resources: self.fetch_resources.bind(this),
        });
    },
           
    fetch_resources : function(callback) {
        var self = this;
        self.ressources = [];
	    ajax.jsonRpc('/booking/assets', 'call', {'category_id':self.category_id}).done(function(assets){
                assets.forEach(function(asset) {
                    self.ressources.push({
                        'id' : asset.id,
                        'title' : asset.name,
                    });
                });
                callback(self.ressources);
                self.trigger_up('switch_ressources', {'ressources' : self.ressources});
            }
        );
    },
    
    fetch_events: function(start, end, timezone, callback) {
        var self = this;
        var self = this;
		self.events = [];
		console.log({
    	    		'asset_id':this.asset_id,
    				'start' : moment(start).format('YYYY-MM-DD HH:mm:ss'),
    				'end' : moment(end).format('YYYY-MM-DD HH:mm:ss'),
    	});
	    ajax.jsonRpc('/booking/events', 'call', {
	    		'category_id':self.category_id,
				'start' : moment(start).format('YYYY-MM-DD HH:mm:ss'),
				'end' : moment(end).format('YYYY-MM-DD HH:mm:ss'),
	    	}).done(function(events){
                events.forEach(function(evt) {
                    self.events.push({
                        'start': moment(evt.start).format('YYYY-MM-DD HH:mm:ss'),
                        'end': moment(evt.stop).format('YYYY-MM-DD HH:mm:ss'),
                        'title': /*evt.partner_id[1] + " - " +*/ evt.name,
                        'allDay': evt.allday,
                        'id': evt.id,
                        'resourceId':evt.room_id[0],
                        'color': evt.recurrency ? '#ffb74d' : '#64b5f6',
                    });
                });
                //console.log([start, end, events])
                callback(self.events);
            }
        );
        
    },
    
    switch_category : function(category) {
        this.category_id = category.id;
        this.$calendar.fullCalendar( 'refetchResources' );
        this.$calendar.fullCalendar( 'refetchEvents' );
    },
    
});

var Browser = Widget.extend({
    template: 'website_booking.browser',
    
    events: {
        "click #add-booking-button": function (event) {
            var self = this;
            event.preventDefault();
            var dialog = new NewBookingDialog(this);
            dialog.appendTo(self.main_modal.empty());
            self.main_modal.modal('open');
        },
    },
    
    custom_events: {
        'switch_category' : 'switch_category',
        'switch_ressources' : 'switch_ressources',
        'newEvent': function(event) {
            this.cal.refetch_events();
        },
    },
    
    renderElement: function() {
        this._super.apply(this, arguments);
        var self = this;
        // Fill navigation panel
        self.nav = new Navigation(this);
        self.nav.appendTo(this.$(".navbar"));
        self.cal = new Calendar(this);
        self.cal.appendTo(this.$(".calendar"));
    },
    
    start: function() {
        this._super.apply(this, arguments);
        var self = this;
        /* TODO : why this.$('#main-modal') does not work ? */
        self.main_modal = this.$('.modal-content').parent().modal();
    },
    
    switch_category: function(event) {
        //console.log('Browser switch_category');
        this.cal.switch_category(event.data.category);
    },
    
    switch_ressources: function(event) {
        if(event.data.ressources.length == 0) {
            this.$('#add-booking-button').addClass('hide');
        } else {
            this.$('#add-booking-button').removeClass('hide');
        }
    },
    
});

core.action_registry.add('website_booking.browser', Browser);

return Browser;

});