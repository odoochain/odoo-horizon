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
    
    init: function(parent) {
        this._super(parent);
        this.today = moment(new Date());
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
    },
    
});

core.action_registry.add('website_booking.browser_mobile', BrowserMobile);

return BrowserMobile;

});