/* global odoo, _, _t */
odoo.define('deliberation.DeliberationController', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');
    var viewRegistry = require('web.view_registry');
    
    var DeliberationController = BasicController.extend({
        
        custom_events: {
            close: '_onClose',
            deliberate_course_group: '_onDeliberateCourseGroup',
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
            var self = this;
            this._rpc({
                model:'school.individual_bloc',
                method:'close_deliberate_bloc',
                args: [ '' ],
                context: this.initialState.context,
            }).then(result => {
                self.do_action(result);
            });
        },
        
        _onDeliberateCourseGroup: function (event) {
            event.stopPropagation();
            console.log("Deliberate CG "+event.data['id']);
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Deliberate Course Group',
                target: 'new',
                flags: { action_buttons: true, headless: true },
                res_model:  'school.course_group_deliberation',
                views: [[false, 'form']],
            });
        },

    });

    return DeliberationController;

});