/* global odoo, _, $ */
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
                $('<div>').addClass('container-fluid o_d_main_container').append(
                    this._renderHeader(),
                ),
                $('<button>').text('Close').click(ev => this.trigger_up('close')),
            );
            return $.when();
        },
        
        _renderHeader : function () {
            var $header = $('<div>').addClass('row');
            var $img = $('<img>')
                .addClass('img img-fluid img-thumbnail ml16')
                //.toggleClass('btn-info', val.view_id[0] === value)
                //.attr('src', val.image)
                //.data('key', val.view_id[0])
                ;
            $header.append($img);
            return $header;
        },
        
    });

    return DeliberationRenderer;

});