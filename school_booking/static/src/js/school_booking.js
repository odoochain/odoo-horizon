odoo.define('school_booking.action_school_booking_main', function (require) {
"use strict";

var core = require('web.core');

var Widget = require('web.Widget');
var Dialog = require('web.Dialog');
var Model = require('web.DataModel');
var data = require('web.data');
var session = require('web.session');

var QWeb = core.qweb;
var _t = core._t;

var BookingAction = Widget.extend({
    template: 'MainView',
    
    events: {
        
        
    },

    init: function(parent, title) {
        
    },

});
   
core.action_registry.add('school_booking.main', BookingAction);

});