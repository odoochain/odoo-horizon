/* global odoo, _ */
odoo.define('deliberation.DeliberationController', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');
    var viewRegistry = require('web.view_registry');

    var DeliberationController = BasicController.extend({
        
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
            event.stopPropagation();
            return this._rpc({
                model:'school.individual_bloc',
                method:'close_deliberate_bloc',
                args: [ ],
            });
        },

    });

    return DeliberationController;

});