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

/* global odoo, $ */

odoo.define('school_evaluations.school_evaluations_program_editor', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var data = require('web.data');
var session = require('web.session');

var Widget = require('web.Widget');
var Dialog = require('web.Dialog');

var QWeb = core.qweb;
var _t = core._t;

var DetailEvalDialog = Dialog.extend({
    template: 'DetailEvalDialog',
    
    events: {
        'change #grade-list': 'changeGrade',
        'change #grade-comment-list': 'changeGradeComment',
    },
    
    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.title = options.title;
        this.program = options.program;
        this.parent = parent;
        this.school_session = parent.school_session;
        this.messages = [
            '',
            'Pertinence et singularité du travail artistique',
            'Qualité particulière du travail artistique',
            'Participation active et régulière aux activités d’enseignement',
            'Caractère accidentel des échecs',
            'Echecs limités en qualité et quantité',
            'Pourcentage global et importance relative des échecs',
            'Progrès réalisés d’une session à l’autre',
            'La réussite des activités de remédiation'
        ];
    },
    
    changeGrade: function() {
        var self = this;
        var grade = this.$('#grade-list').val()
        rpc.query({
                model: 'school.individual_program',
                method: 'write',
                args: [self.program.id,{'grade':grade}],
            }).then(function(result){
            self.program.grade = grade;
            self.parent.update(); 
        })
    },
    
    changeGradeComment: function() {
        var self = this;
        var mess_idx = parseInt(this.$('#grade-comment-list').val());
        var message = this.messages[mess_idx];
        rpc.query({
                model: 'school.individual_program',
                method: 'write',
                args: [self.program.id,{'grade_comments':message}],
            }).then(function(result){
            self.program.grade_comments = message;
            self.parent.update();
        })
    },
    
});

return Widget.extend({
    template: "ProgramEditor",
    
    events: {
        "click .btn_moyenne": function (event) {
            var self = this;
            event.preventDefault();
            new DetailEvalDialog(this, {title : _t('Detailed Evaluation'), program : self.program}).open();
        },
        
        "click .btn-award": function (event) {
            event.preventDefault();
            var self = this;
            rpc.query({
                model: 'school.individual_program',
                method: "set_to_awarded",
                args: [self.datarecord.id,self.dataset.get_context(),self.parent.year_id],
            }).then(function(result) {
                self.parent.$(".o_school_bloc_item.active i").removeClass('fa-user');
                self.parent.$(".o_school_bloc_item.active i").addClass('fa-check');
                self.next().then(function(){
                    self.parent.$('.o_school_bloc_item.active').removeClass('active');
                    self.parent.$("a[data-bloc-id='" + self.datarecord.id + "']").addClass('active');
                });
            });
        },
    },
    

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
        
        return rpc.query({
                model: 'school.individual_program',
                method: "compute_evaluation_details",
                args: [self.program.id],
            }).then(
                function(results){
                    self.program.evaluation_details = results;
                }).then(
                    function() {
                        return rpc.query({
                                model: 'school.individual_bloc',
                                method: 'search_read',
                                domain: [['program_id','=',self.program.id]],
                                fields: [],
                            }).then(
                            function(blocs) {
                                self.course_groups = [];
                                return rpc.query({
                                    model: 'school.individual_course_group',
                                    method: 'search_read',
                                    domain: [['bloc_id', 'in', blocs.map(function(b){return b.id})],['is_ghost_cg','=',false]],
                                    fields: ['id','name','title','course_ids','dispense','final_result_bool','acquiered','year_id','first_session_computed_result','first_session_deliberated_result_bool','second_session_computed_result','second_session_deliberated_result_bool','second_session_result_bool','final_result','total_credits','total_weight'],
                                    order: 'year_id desc, sequence'
                                }).then(
                                    function(course_groups) {
                                        self.course_groups = self.course_groups.concat(course_groups);
                                    });
                            });
                    })
    },
    
})});