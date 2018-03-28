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
    
    
    
});

core.action_registry.add('website_booking.browser_mobile', BrowserMobile);

return BrowserMobile;

});