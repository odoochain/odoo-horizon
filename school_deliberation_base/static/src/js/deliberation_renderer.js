/* global odoo, _, $ */
odoo.define('deliberation.DeliberationRenderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var utils = require('web.utils');
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
            var $header = $('<div>',{class : 'row bloc_header mt-4'});
            var $col1 = $('<div>',{class : 'col-2'});
            var $img = $('<img>')
                .addClass('img img-fluid img-thumbnail ml16')
                .attr('src', this._getImageURL('res.partner','image_256',record.student_id.data.id,'student picture'))
                .data('key', record.id);
            $col1.append($img);
            $header.append($col1);
            var $col2 = $('<div>',{class : 'col-10'});
            $col2.append(`
                        <div class="row">
                        <span class="col-md-10" style="min-height:66px;">
                            <h1>${record.student_id.data.display_name} - Bachelier en musique : Guitare - 3</h1>
                        </span>
                        <span class="col-md-2 refresh_button">
                            <button class="btn btn-default o_reload_bloc" type="button">
                                <i class="fa fa-refresh fa-fw"></i>
                            </button>
                        </span>
                    </div>`);
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