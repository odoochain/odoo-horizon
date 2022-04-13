/* global odoo, _ */
odoo.define('deliberation.DeliberationView', function (require) {
    "use strict";

    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');
    var DeliberationController = require('deliberation.DeliberationController');
    var DeliberationModel = require('deliberation.DeliberationModel');
    var DeliberationRenderer = require('deliberation.DeliberationRenderer');


    var DeliberationView = AbstractView.extend({
        display_name: 'Deliberation',
        icon: 'fa-pagelines',
        cssLibs: [
            '/deliberation/static/src/css/deliberation.css',
        ],
        config: _.extend({},AbstractView.prototype.config, {
            Model: DeliberationModel,
            Controller: DeliberationController,
            Renderer: DeliberationRenderer,
        }),
        viewType: 'deliberation',
        groupable: false,
        init: function () {
            this._super.apply(this, arguments);
        },
    });
    view_registry.add('deliberation', DeliberationView);
    return DeliberationView;
});