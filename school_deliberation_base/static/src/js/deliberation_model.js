/* global odoo, _ */
odoo.define('deliberation.DeliberationModel', function (require) {
    "use strict";

    var BasicModel = require('web.BasicModel');

    var DeliberationModel = BasicModel.extend({

        /**
         * @private
         * @param {Object} record
         * @param {string} fieldName
         * @returns {Promise}
         */
        _fetchProgram: function (record, fieldName) {
            return this._rpc({
                model: 'school.individual_program',
                method: 'search_read',
                domain: [['id','=',record.program_id]],
                fields: [],
            }).then(function (result) {
                return result;
            });
        },
          
    });
    return DeliberationModel;
});