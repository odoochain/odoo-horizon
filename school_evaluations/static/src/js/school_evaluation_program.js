/*
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
*/
odoo.define('school_evaluations.school_evaluations_program_editor', function (require) {
"use strict";

var config = require('web.config');
var form_common = require('web.form_common');
var core = require('web.core');
var data = require('web.data');
var session = require('web.session');

var Widget = require('web.Widget');
var Model = require('web.DataModel');
var Dialog = require('web.Dialog');

var QWeb = core.qweb;
var _t = core._t;

return Widget.extend({
    template: "ProgramEditor",
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        this.title = title;
        this.parent = parent;
    },
    
    start: function() {
        this.dataset = new data.DataSet(this, 'school.individual_program', new data.CompoundContext());
        this.program = false;
    },
    
    read_ids: function(ids,idx) {
        var self = this;
        this.school_session = this.parent.school_session;
        idx = idx || 0;
        return this.dataset.read_ids(ids,[]).then(function (results) {
                self.ids = ids;
                self.records = results;
                self.record_idx = idx;
                self.datarecord = self.records[self.record_idx];
            });
    },  
    
    set_bloc_id: function(bloc_id) {
        var self = this;
        this.program_id = bloc_id;
        for (var i=0, ii=self.records.length; i<ii; i++) {
            if(this.records[i].id == this.program_id){
                this.record_idx = i;
                this.datarecord = this.records[this.record_idx];
                return self.update();
            }
        }
    },
    
    next: function() {
        var self = this;
        if(this.record_idx < this.records.length-1){
            this.record_idx += 1;
            this.datarecord = this.records[this.record_idx];
            return self.update();
        } else {
            return self.update();
        }
        
    },
    
    update: function() {
        var self = this;
        return self.read_ids(self.ids,self.record_idx).then(function(){
            self.program = self.datarecord;
            self._read_program_data().done(
                function(){
                    self.parent.hide_startup();
                    self.renderElement();
                });
        });
    },
    
    _read_program_data: function(){
        var self = this;
        
        self.student_image = session.url('/web/image', {
            model: 'res.partner',
            id: self.program.student_id[0],
            field: 'image_medium',
            unique: (self.datarecord.__last_update || '').replace(/[^0-9]/g, '')
        });
        
        switch (self.program.grade) {
          case "without":
            self.program.grade_text = "Sans grade";
            break;
          case "satisfaction":
            self.program.grade_text = "Satisfaction";
            break;
          case "distinction":
            self.program.grade_text = "Distinction";
            break;
          case "second_class":
            self.program.grade_text = "la Grande Distinction";
            break;
          case "first_class":
            self.program.grade_text = "la Plus Grande Distinction";
            break;
        };
        
        return new Model('school.individual_program').call('compute_evaluation_details', [self.program.id]).then(
                function(results){
                    self.program.evaluation_details = results;
                }).then(
                    function() {
                        return new Model('school.individual_bloc').query().filter([['program_id','=',self.program.id]]).all().then(
                            function(blocs) {
                                self.course_groups = [];
                                return new Model('school.individual_course_group')
                                    .query(['id','name','title','course_ids','dispense','final_result_bool','acquiered','year_id','first_session_computed_result','first_session_deliberated_result_bool','second_session_computed_result','second_session_deliberated_result_bool','second_session_result_bool','final_result','total_credits','total_weight'])
                                    .filter([['bloc_id', 'in', blocs.map(function(b){return b.id})]])
                                    .order_by('year_id desc, sequence')
                                    .all().then(
                                    function(course_groups) {
                                        self.course_groups = self.course_groups.concat(course_groups);
                                    });
                            });
                    })
    },
    
})});