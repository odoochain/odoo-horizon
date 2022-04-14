/* global odoo, _, $ */
odoo.define('deliberation.DeliberationRenderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var CharImageUrl = require('web.basic_fields').CharImageUrl;
    // var core = require('web.core');
    // var qweb = core.qweb;

    var DeliberationRenderer = BasicRenderer.extend({
        events: _.extend({}, BasicRenderer.prototype.events, {
        }),
        _render: function () {
            this.$el.append(
                $('<div>').addClass('container-fluid o_d_main_container').append(
                    this._renderHeader(),
                ),
                $('<button>').text('Close').click(ev => this.trigger_up('close')),
            );
            return $.when();
        },
        
        _renderHeader : function () {
            var record = this.state.data;
            var $header = $('<div>').addClass('row');
            var imageField = new CharImageUrl(this, 'image_1920', record.student_id);
            imageField.renderTo($header);
            return $header;
        },
        
    });

    return DeliberationRenderer;

});