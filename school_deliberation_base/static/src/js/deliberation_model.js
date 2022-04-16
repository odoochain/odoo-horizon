/* global odoo, _ */
odoo.define('deliberation.DeliberationModel', function (require) {
    "use strict";

    var BasicModel = require('web.BasicModel');

    var DeliberationModel = BasicModel.extend({

        /**
         * Applies the forecast logic to the domain and context if needed before the read_group.
         * After the read_group, checks the end date of the last displayed group in order to be able to
         * add the next group with the ForecastColumnQuickCreate widget
         *
         * @private
         * @override
         */
        async __load(params) {
            var self = this;
            return this._super(...arguments).then(function () {
                self._fetchProgram()
            });
        },
        
        /**
         * Applies the forecast logic to the domain and context if needed before the read_group.
         * After the read_group, checks the end date of the last displayed group in order to be able to
         * add the next group with the ForecastColumnQuickCreate widget
         *
         * @private
         * @override
         */
        async __reload(id, params) {
            var self = this;
            return this._super(...arguments).then(function () {
                self._fetchProgram()
            });
        },

        /**
         * @private
         * @returns {Promise}
         */
        _fetchProgram: function () {
            var self = this;
            return this._rpc({
                model: "school.individual_program", 
                method: "read", 
                args: [[this.state.data.program_id.res_id]]
            }).then(result => { 
                self.state.program = result;
            });
        },
          
    });
    return DeliberationModel;
});