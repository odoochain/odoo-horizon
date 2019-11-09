odoo.define('website_horizon_responsive.main', function (require) {
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

ajax.loadXML('/website_horizon_responsive/static/src/xml/main.xml', qweb);

var Main = Widget.extend({
    template: 'website_horizon_responsive.index',
    
    events: {
        "click #add-booking-button": function (event) {
            var self = this;
            event.preventDefault();
        },
    },
    
    init : function() {
        this._super.apply(this, arguments);
        var self = this;
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
                self.avatar_src = session.url('/web/image', {model:'res.users', field: 'image_small', id: session.uid});
                self.$el.html(qweb.render('website_booking.toolbar_log', {widget : self}));
                self.$el.openFAB();
            } else {
                self.$el.html(qweb.render('website_booking.toolbar_nolog', {widget : self}));
            }
        });
    },
    
    renderElement: function() {
        this._super.apply(this, arguments);
        this._current_state = $.deparam(window.location.hash.substring(1));
        var self = this;
    },
    
});

core.action_registry.add('website_horizon_responsive.main', Main);

return Main;

});