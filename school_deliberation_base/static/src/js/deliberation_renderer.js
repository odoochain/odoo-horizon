/* global odoo, _, $ */
odoo.define('deliberation.DeliberationRenderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var utils = require('web.utils');
    // var core = require('web.core');
    // var qweb = core.qweb;

    var DeliberationRenderer = BasicRenderer.extend({
        
        specialData: "_fetchProgram",
        
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
            var program = this.specialData;
            var $header = $('<div>',{class : 'row bloc_header mt-4'});
            var $col1 = $('<div>',{class : 'col-2'});
            var $img = $('<img>',{ 
                'class' : 'img img-fluid img-thumbnail ml16',
                'src' : this._getImageURL('res.partner','image_256',record.student_id.data.id,'student picture'),
                'style' : 'min-height: 256px;',
            });
            $col1.append($img);
            $header.append($col1);
            var $col2 = $('<div>',{class : 'col-10'});
            $col2.append(`
                    <div class="row">
                        <span class="col-md-10">
                            <h1 class="display-4">${record.student_id.data.display_name}</h1>
                        </span>
                        <span class="col-md-2 refresh_button">
                            <button class="btn btn-default o_reload_bloc" type="button">
                                <i class="fa fa-refresh fa-fw fa-2x"></i>
                            </button>
                        </span>
                    </div>
                    <div class="row">
                        <span class="col">
                            <h1 class="display-5">${record.source_bloc_title} - ${record.source_bloc_level}</h1>
                        </span>
                    </div>
                    <div class="row vertical-align" style="margin-bottom: 10px;">
                        <div class="col-md-2">
                            <button class="btn btn_credits" type="button">
                                <h1 class="display-5">PAE</h1><br/><span class="score_value">${record.total_acquiered_credits}/${record.total_credits}</span>
                            </button>
                        </div>
                        <div class="col-md-8">
                        </div>
                        <div class="col-md-2">
                        </div>
                    </div>
            `);
            switch (record.source_bloc_level) {
                case 1 :
                    $col2.append(`
                    <div class="row vertical-align">
                        <div class="progress" style="width:100%;">
                            <div class="progress-bar progress-bar-info" style="width:${program.total_acquiered_credits)/Math.max(program.required_credits,program.total_registered_credits)*100}%">
                                ${program.total_acquiered_credits}
                            </div>
                            <div class="progress-bar progress-bar-success" t-att-style="'width:'+(-widget.bloc.total_dispensed_credits+widget.bloc.total_acquiered_credits)/Math.max(widget.program.required_credits,widget.program.total_registered_credits)*100+'%'">
                                ${record.total_acquiered_credits}
                            </div>
                            <div t-if="widget.bloc.total_credits-widget.bloc.total_acquiered_credits > 0" class="progress-bar progress-bar-warning" t-att-style="'width: '+${record.total_credits-widget.bloc.total_acquiered_credits)/Math.max(widget.program.required_credits,widget.program.total_registered_credits)*100+'%'">
                                <span t-esc="${record.total_credits-widget.bloc.total_acquiered_credits)"/>
                            </div>
                            </t>
                        </div>
                    </div>
                    `);
                case 2 :
                case 3 :
                    $col2.append(`
                    <div class="row vertical-align">
                        <div class="progress" style="width:100%;">
                            <div class="progress-bar progress-bar-info" t-att-style="'width: '+${record.total_dispensed_credits+widget.program.total_acquiered_credits)/Math.max(widget.program.required_credits,widget.program.total_registered_credits)*100+'%'">
                                <span t-esc='${record.total_dispensed_credits+widget.program.total_acquiered_credits)'/>
                            </div>
                            <t t-if="${record.state != 'awarded_first_session') and ${record.state != 'awarded_second_session')">
                            <div class="progress-bar progress-bar-success" t-att-style="'width: '+(-widget.bloc.total_dispensed_credits+widget.bloc.total_acquiered_credits)/Math.max(widget.program.required_credits,widget.program.total_registered_credits)*100+'%'">
                                <span t-esc='(-widget.bloc.total_dispensed_credits+widget.bloc.total_acquiered_credits)'/>
                            </div>
                            <div t-if="widget.bloc.total_credits-widget.bloc.total_acquiered_credits > 0" class="progress-bar progress-bar-warning" t-att-style="'width: '+${record.total_credits-widget.bloc.total_acquiered_credits)/Math.max(widget.program.required_credits,widget.program.total_registered_credits)*100+'%'">
                                <span t-esc="${record.total_credits-widget.bloc.total_acquiered_credits)"/>
                            </div>
                            </t>
                        </div>
                    </div>
                    `);
                case 4 :
                case 5 :
                    $col2.append(`
                    <div class="row vertical-align">
                        <div class="progress" style="width:100%;">
                            <div class="progress-bar progress-bar-info" t-att-style="'width: '+${record.total_dispensed_credits+widget.program.total_acquiered_credits)/Math.max(widget.program.required_credits,widget.program.total_registered_credits)*100+'%'">
                                <span t-esc='${record.total_dispensed_credits+widget.program.total_acquiered_credits)'/>
                            </div>
                            <t t-if="${record.state != 'awarded_first_session') and ${record.state != 'awarded_second_session')">
                            <div class="progress-bar progress-bar-success" t-att-style="'width: '+(-widget.bloc.total_dispensed_credits+widget.bloc.total_acquiered_credits)/Math.max(widget.program.required_credits,widget.program.total_registered_credits)*100+'%'">
                                <span t-esc='(-widget.bloc.total_dispensed_credits+widget.bloc.total_acquiered_credits)'/>
                            </div>
                            <div t-if="widget.bloc.total_credits-widget.bloc.total_acquiered_credits > 0" class="progress-bar progress-bar-warning" t-att-style="'width: '+${record.total_credits-widget.bloc.total_acquiered_credits)/Math.max(widget.program.required_credits,widget.program.total_registered_credits)*100+'%'">
                                <span t-esc="${record.total_credits-widget.bloc.total_acquiered_credits)"/>
                            </div>
                            </t>
                        </div>
                    </div>
                    `);
            }
            $header.append($col2);
            return $header;
        },
        
        /**
         * @private -- FROM KANBAN SOURCE COPYRIGHT ODOO
         * @param {string} model the name of the model
         * @param {string} field the name of the field
         * @param {integer} id the id of the resource
         * @param {string} placeholder
         * @returns {string} the url of the image
         */
        _getImageURL: function (model, field, id, placeholder) {
            id = (_.isArray(id) ? id[0] : id) || null;
            var isCurrentRecord = this.modelName === model && (this.recordData.id === id || (!this.recordData.id && !id));
            var url;
            if (isCurrentRecord && this.record[field] && this.record[field].raw_value && !utils.is_bin_size(this.record[field].raw_value)) {
                // Use magic-word technique for detecting image type
                url = 'data:image/' + this.file_type_magic_word[this.record[field].raw_value[0]] + ';base64,' + this.record[field].raw_value;
            } else if (placeholder && (!model || !field || !id || (isCurrentRecord && this.record[field] && !this.record[field].raw_value))) {
                url = placeholder;
            } else {
                var session = this.getSession();
                var params = {
                    model: model,
                    field: field,
                    id: id
                };
                if (isCurrentRecord) {
                    params.unique = this.record.__last_update && this.record.__last_update.value.replace(/[^0-9]/g, '');
                }
                url = session.url('/web/image', params);
            }
            return url;
        },
        
    });

    return DeliberationRenderer;

});