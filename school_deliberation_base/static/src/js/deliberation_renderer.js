/* global odoo, _ */
odoo.define('deliberation.DeliberationRenderer', function (require) {
    "use strict";

    var AbstractRenderer = require('web.BasicRenderer');
    // var core = require('web.core');
    // var qweb = core.qweb;

    var DeliberationRenderer = AbstractRenderer.extend({
        events: _.extend({}, AbstractRenderer.prototype.events, {
        }),
        _render: function () {
            this.$el.append(
                    $('<h1 class="o_d_title">').text('Hello World!'),
            );
            return $.when();
        },
        
    });

    return DeliberationRenderer;

});