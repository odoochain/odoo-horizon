odoo.define('website_booking.browser', function (require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var BaseWidget = require('website_booking.BaseWidget');
var Model = require('web.DataModel');

var _t = core._t;
var QWeb = core.qweb;

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

var Browser = BaseWidget.extend({
    template: 'Browser',
    
    init: function(parent, options) {
        this._super(parent, options);
    },
    
    start: function() {
        var self = this;
        self.$calendar = this.$("#calendar");
        self.$calendar.fullCalendar({
    			header: {
    				left: 'prev,next today',
    				center: 'title',
    				right:'',
    			},
    			height: 800,
    			locale: 'fr',
    			defaultDate: moment(),
    			defaultView: 'agendaDay',
    			minTime: "07:00:00",
    			maxTime: "20:00:00",
    			navLinks: true, // can click day/week names to navigate views
    			editable: true,
    			eventLimit: true, // allow "more" link when too many events
    			events: function(start, end, timezone, callback){
                            var extend_domain = [[this.date_start, '<=', moment_to_str(end)]];
                            if (this.date_stop) {
                                extend_domain.push([this.date_stop, '>=', moment_to_str(start)]);
                            } else if (!this.date_delay) {
                                extend_domain.push([this.date_start, '>=', moment_to_str(start)]);
                            }
                            extend_domain.push(['buiding_id', '=', 1]);
                            // read_slice is launched uncoditionally, when quickly
                            // changing the range in the calender view, all of
                            // these RPC calls will race each other. Because of
                            // this we keep track of the current range of the
                            // calendar view.
                            self.current_start = start.toDate();
                            self.current_end = end.toDate();
                            self.dataset.read_slice(['id', 'name','start','stop','allday','asset_id','partner_id'], {
                                offset: 0,
                                domain: extend_domain,
                                context: {},
                            }).done(function(events) {
                                // undo the read_slice if it the range has changed since it launched
                                if (self.current_start.getTime() != start.toDate().getTime() || self.current_end.getTime() != end.toDate().getTime()) {
                                    self.dataset.ids = self.previous_ids;
                                    return;
                                }
                                self.previous_ids = self.dataset.ids.slice();
                                if (self.dataset.index === null) {
                                    if (events.length) {
                                        self.dataset.index = 0;
                                    }
                                } else if (self.dataset.index >= events.length) {
                                    self.dataset.index = events.length ? 0 : null;
                                }
                                var fc_events = [];
                                for (var evt_id in events) {
                                    var evt = events[evt_id];
                                    var r = {
                                        'start': moment(evt.start).format('YYYY-MM-DD HH:mm:ss'),
                                        'end': moment(evt.stop).format('YYYY-MM-DD HH:mm:ss'),
                                        'title': evt.partner_id[1] + " - " + evt.name,
                                        'allDay': evt.allday,
                                        'id': evt.id,
                                        'resourceId':evt.asset_id[0],
                                    };
                                    fc_events.push(r);
                                }
                                callback(fc_events);
                            });
    			},
    			resources: function(callback) {
    			    self.resourceObjects = [];
    			    self.scheduler_domain = [['building_id', '=', 1]];
                    new Model('school.asset').query(["name"]).filter(self.scheduler_domain).all().then(function(result) {
                        _.each(result, function(item) {
                            self.resourceObjects.push({
                                id : item.id,
                                title : item.name,
                            });
                        });
                    }).done(function() {
                        callback(self.resourceObjects);
                    });
                },
                refetchResourcesOnNavigate : false,
    		});
    		setTimeout(function() {
                    self.$calendar.fullCalendar('changeView');
                }, 100);
    },
    
});

core.action_registry.add('website_booking.browser', Browser);

});