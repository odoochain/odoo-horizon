/* global odoo, _, _t */
odoo.define('deliberation.DeliberationController', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');
    var viewRegistry = require('web.view_registry');
    
    const KanbanController = require('web.KanbanController');

    KanbanController.include({

        /**
         * @override
         * @private
         */
        _onOpenRecord() {
            console.log(this);
            
            this.getParent().state.res_ids
            
            if (this.$el.hasClass('o_deliberation_bloc_kanban')) {
                var self = this;
                console.log("Deliberate Bloc "+this.id);
                this._rpc({
                    model:'school.individual_bloc',
                    method:'action_deliberate_bloc',
                    args: [ [this.id] ],
                    context: {...this.state.context,...{
                        active_ids : this.getParent().state.res_ids,
                    }},
                }).then(result => {
                    self.do_action(result);
                });
                
                
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
    
    var DeliberationController = BasicController.extend({
        
        custom_events: {
            close: '_onClose',
            deliberate_course_group: '_onDeliberateCourseGroup',
            reload_bloc: '_onReloadBloc',
            deliberate_next_bloc: '_onNextBloc',
            deliberate_previous_bloc: '_onPreviousBloc',
        },

        init: function (parent, model, renderer, params) {
            this.model = model;
            this.renderer = renderer;
            this._super.apply(this, arguments);
        },

        start: function () {
            this.current_index = 0;
            this.max_index = 10;
            return this._super();
        },

        _onReloadBloc: function (event) {
            this.reload();
        },
        
        _onPreviousBloc: function (event) {
            console.log(this);
        },
        
        _onNextBloc: function (event) {
            console.log(this);
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
            var self = this;
            console.log("Deliberate CG "+event.data['id']);
            this._rpc({
                model:'school.individual_bloc',
                method:'action_deliberate_course_group',
                args: [ [self.id] ],
                context: {...self.initialState.context,...{
                    default_course_group_id: parseInt(event.data['id']),
                    default_deliberation_id: parseInt(self.initialState.context['deliberation_id']),
                }},
            }).then(result => {
                self.do_action(result, { 'on_close' : self._onReloadBloc.bind(self) });
            });
            
            /*this.do_action({
                type: 'ir.actions.act_window',
                name: 'Deliberate Course Group',
                target: 'new',
                flags: { action_buttons: true, headless: true },
                res_model:  'school.course_group_deliberation',
                context: {
                    default_course_group_id: parseInt(event.data['id']),
                    default_deliberation_id: parseInt(this.initialState.context['deliberation_id']),
                },
                views: [[false, 'form']],
            });*/
        },

    });

    return DeliberationController;

});