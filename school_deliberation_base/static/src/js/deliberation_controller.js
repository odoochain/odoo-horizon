/* global odoo, _ */
odoo.define('deliberation.DeliberationController', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');


    var DeliberationController = AbstractController.extend({
        
        custom_events: {
            close: '_onClose'
        },

        init: function (parent, model, renderer, params) {
            this.model = model;
            this.renderer = renderer;
            this._super.apply(this, arguments);
        },

        start: function () {
            return this._super();
        },

        _onClose: function (event) {
            this.trigger_up("history_back");
        },

    });

    return DeliberationController;

});