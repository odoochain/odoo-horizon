odoo.define('website_booking.browser', function (require) {
"use strict";

/* global moment, time */

var core = require('web.core');
var ajax = require('web.ajax');
var Widget = require('web.Widget');
var Dialog = require("web.Dialog");

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

var MDLWidget = Widget.extend({
    
    start: function () {
        this._super.apply(this, arguments);
        componentHandler.upgradeElements(this.$el);
    },
    
});

var NewBookingDialog = Dialog.extend({
    template: 'website_booking.new_booking_dialog',
    
    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.ressources = parent.ressources;
    },
    
    start: function () {
        this._super.apply(this, arguments);
        componentHandler.upgradeElements(this.$el);
    },
});

var NavigationCard = MDLWidget.extend({
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
        this.getParent().$el.find('.navbar-card.mdl-shadow--8dp').removeClass('mdl-shadow--8dp').addClass('mdl-shadow--2dp')
        this.$el.find('.navbar-card').removeClass('mdl-shadow--2dp').addClass('mdl-shadow--8dp');
    },
    
});

var Navigation = MDLWidget.extend({
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
        console.log("Navigator switch_category");
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

var Calendar = MDLWidget.extend({
    template: 'website_booking.browser_calendar',

    renderElement: function() {
        this._super.apply(this, arguments);
        var self = this;
        self.$calendar = this.$el;
        self.$calendar.fullCalendar({
			header: {
				left: 'prev,next today',
				center: 'title',
				right:'',
			},
			editable: false,
			height: 640,
			locale: 'fr',
			titleFormat: 'dddd, D MMMM',
			defaultDate: moment(),
			defaultView: 'agendaDay',
			minTime: "07:00:00",
			maxTime: "20:00:00",
			navLinks: true, // can click day/week names to navigate views
			editable: true,
			eventLimit: true, // allow "more" link when too many events
			events: self.fetch_events.bind(this),
			resources: self.fetch_resources.bind(this),
            refetchResourcesOnNavigate : false,
		});
    },
    
    start : function() {
        this._super.apply(this, arguments);
        var self = this;
        // Force a refresh to get it right
        setTimeout(function() {
            self.$calendar.fullCalendar('changeView');
            self.$('.fc-button').removeClass('fc-button').addClass('mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-color--accent mdl-color-text--accent-contrast');
            componentHandler.upgradeElements(self.$calendar);
        }, 100);
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
            }
        );
    },
    
    fetch_events: function(start, end, timezone, callback) {
        var self = this;
        var self = this;
		self.events = [];
	    ajax.jsonRpc('/booking/events', 'call', {
	    		'category_id':self.category_id,
				'start' : start,
				'end' : end,
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
        
    },
    
    switch_category : function(category) {
        console.log('Calendar switch_category ' + category.name);
        this.category_id = category.id;
        this.$calendar.fullCalendar( 'refetchResources' );
        this.$calendar.fullCalendar( 'refetchEvents' );
    },
            
});

var Browser = MDLWidget.extend({
    template: 'website_booking.browser',
    
    events: {
        "click #add-booking-button": function (event) {
            var self = this;
            event.preventDefault();
            new NewBookingDialog(this, {title : _t('New Booking')}).open();
        },
    },
    
    custom_events: {
        'switch_category' : 'switch_category',    
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
    
    switch_category: function(event) {
        //console.log('Browser switch_category');
        this.cal.switch_category(event.data.category);
    },
    
});

core.action_registry.add('website_booking.browser', Browser);

return Browser;

});