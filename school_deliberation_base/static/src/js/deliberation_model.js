/* global odoo, _ */
odoo.define('deliberation.DeliberationModel', function (require) {
    "use strict";

    var BasicModel = require('web.BasicModel');

    var DeliberationModel = BasicModel.extend({

        /**
         * @override
         */
        init: function () {
            this.programValues = {};
            this._super.apply(this, arguments);
        },
    
        /**
         * @override
         */
        __get: function (localID) {
            var result = this._super.apply(this, arguments);
            if (_.isObject(result)) {
                result.programValues = this.programValues[localID];
            }
            return result;
        },

        /**
         * @override
         * @returns {Promise}
         */
        __load: function () {
            return this._loadProgram(this._super.apply(this, arguments));
        },
        /**
         * @override
         * @returns {Promise}
         */
        __reload: function () {
            return this._loadProgram(this._super.apply(this, arguments));
        },
    
        /**
         * @private
         * @param {Promise} super_def a promise that resolves with a dataPoint id
         * @returns {Promise -> string} resolves to the dataPoint id
         */
        _loadProgram: function (super_def) {
            var self = this;
            return Promise.all([super_def.then(function(results) {
                var localID = results;
                self._rpc({
                    model: "school.individual_program", 
                    method: "read", 
                    args: [[self.localData[self.localData[localID].data.program_id].data.id]],
                }).then(function(result){
                    self.dashboardValues[localID] = result;
                    return localID;
                })})]);
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
                args: [[this.localData[this.localData['school.individual_bloc_1'].data.program_id].data.id]],
            }).then(result => { 
                self.state.program = result;
            });
        },
          
    });
    return DeliberationModel;
});