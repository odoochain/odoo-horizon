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

odoo.define('school_evaluations.school_evaluations_bloc_editor', function (require) {
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
        });
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
        });
    },
    
});

var DetailResultDialog = Dialog.extend({
    template: 'DetailResultDialog',
    
    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.title = options.title;
        this.course_group = options.course_group;
        this.parent = parent;
        this.school_session = parent.school_session;
    },
    
});

var DeliberateCourseGroupDialog = Dialog.extend({
    template: 'DeliberateCourseGroupDialog',
    
    events: {
        'change #comment-list': 'change_message',
    },
    
    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.title = options.title;
        this.course_group = options.course_group;
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
        this.message = '';
        this.set_buttons([
        {
            text: _t("Ok"),
            classes: 'btn-primary',
            close: true,
            click: this.confirm_callback
        },
        {
            text: _t("Cancel"),
            close: true,
            click: this.cancel_callback
        }]);
    },
    
    change_message: function() {
        var self = this;
        self.message = this.$('#comment-list').val();
    },
    
    confirm_callback: function() {
        var self=this;
        rpc.query({
            model: 'school.individual_course_group',
            method: "set_deliberated_to_ten",
            args: [self.course_group.id,self.school_session, self.messages[self.message]],
        }).then(function(result) {
            self.parent.update();
        });
    }
});

return Widget.extend({
    template: "BlocEditor",
    events: {
        "click .bloc_award": function (event) {
            event.preventDefault();
            var self = this;
            rpc.query({
                model: 'school.individual_bloc',
                method: this.school_session == 1 ? "set_to_awarded_first_session" : "set_to_awarded_second_session",
                args: [self.datarecord.id,self.bloc_result.message],
            }).then(function(result) {
                self.parent.$(".o_school_bloc_item.active i").removeClass('fa-user');
                self.parent.$(".o_school_bloc_item.active i").addClass('fa-check');
                if (this.school_session == 1) {
                    self.bloc.state = "awarded_first_session";
                } else {
                    self.bloc.state = "awarded_second_session";
                }
                self.next().then(function(){
                    self.parent.$('.o_school_bloc_item.active').removeClass('active');
                    self.parent.$("a[data-bloc-id='" + self.datarecord.id + "']").addClass('active');
                });
            });
        },

        "click .bloc_postpone": function (event) {
            event.preventDefault();
            var self = this;
            rpc.query({
                model: 'school.individual_bloc',
                method: "set_to_postponed",
                args: [self.datarecord.id,self.bloc_result.message,],
            }).then(function(result) {
                self.parent.$(".o_school_bloc_item.active i").removeClass('fa-user');
                self.parent.$(".o_school_bloc_item.active i").addClass('fa-check');
                self.bloc.state = "postponed";
                self.next().then(function(){
                    self.parent.$('.o_school_bloc_item.active').removeClass('active');
                    self.parent.$("a[data-bloc-id='" + self.datarecord.id + "']").addClass('active');
                });
            });
        },

        "click .bloc_failed": function (event) {
            event.preventDefault();
            var self = this;
            rpc.query({
                model: 'school.individual_bloc',
                method: "set_to_failed",
                args: [self.datarecord.id,self.bloc_result.message,],
            }).then(function(result) {
                self.parent.$(".o_school_bloc_item.active i").removeClass('fa-user');
                self.parent.$(".o_school_bloc_item.active i").addClass('fa-check');
                self.bloc.state = "failed";
                self.next().then(function(){
                    self.parent.$('.o_school_bloc_item.active').removeClass('active');
                    self.parent.$("a[data-bloc-id='" + self.datarecord.id + "']").addClass('active');
                });
            });
        },
        
        "click .o_school_edit_icg": function (event) {
            var self = this;
            event.preventDefault();
            var id = this.$(event.currentTarget).data('cg-id');
            var res_id = parseInt(id).toString() == id ? parseInt(id) : id;
            new DetailResultDialog(this, {title : _t('Detailed Results'), course_group : self.course_groups[self.course_group_id_map[res_id]]}).open();
        },
        
        "click .o_reload_bloc": function (event) {
            var self = this;
            event.preventDefault();
            self.refresh();
        },
        
        "click .o_set_delib": function (event) {
            var self = this;
            var cg_id = $(event.target).data('course-group-id');
            event.preventDefault();
            new DeliberateCourseGroupDialog(this, {title : _t('Deliberate Course Group'), course_group : self.course_groups[self.course_group_id_map[cg_id]]}).open();
        },
    },
    
    init: function(parent, title) {
        this._super.apply(this, arguments);
        this.title = title;
        this.parent = parent;
        this.records = false;
        this.dataset = new data.DataSet(this, 'school.individual_bloc', {});
        this.bloc = false;
    },
    
    read_ids: function(ids,idx) {
        var self = this;
        this.school_session = this.parent.school_session;
        idx = idx || 0;
        return this.dataset.read_ids(ids,[]).then(function (results) {
            self.ids = ids;
            self.records = results;
        });
            
    },
    
    set_bloc_id: function(bloc_id) {
        var self = this;
        this.bloc_id = bloc_id;
        for (var i=0, ii=self.records.length; i<ii; i++) {
            if(this.records[i].id == bloc_id){
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
    
    refresh: function() {
        var self = this;
        return self.read_ids(self.ids,self.record_idx).then(function(){
            self.bloc = self.datarecord = self.records[self.record_idx];
            self._read_bloc_data().then(
                function(){
                    self.parent.hide_startup();
                    self.renderElement();
                });
        });
    },
    
    update: function() {
        var self = this;
        if(!this.records) {
            return self.read_ids(self.ids,self.record_idx).then(function(){
                self.bloc = self.datarecord = self.records[self.record_idx];
                self._read_bloc_data().then(
                    function(){
                        self.parent.hide_startup();
                        self.renderElement();
                    });
            });
        } else {
            self.bloc = self.datarecord = self.records[self.record_idx];
            return self._read_bloc_data().then(
                function(){
                    self.parent.hide_startup();
                    self.renderElement();
                });
        }
    },
    
    _update_evaluation_messages: function() {
        var self = this;
        
        if(self.school_session == 1) {
            if (self.bloc.total_acquiered_credits >= self.bloc.total_credits) {
                self.bloc_result = {
                            'message' : _t("A validé tous les crédits ECTS de son PAE."),
                            'class' : "success",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                }
            } else {
                self.bloc_result = {
                    'message' : _t("N'a pas validé tous les crédits ECTS de son PAE et est ajourné(e)."),
                    'class' : "danger",
                    'button_text' : _t("Ajourné"),
                    'next_action' : "postpone",
                };
            } 
        } else {
            switch(self.bloc.source_bloc_level) {
                case "1" :
                    if(self.bloc.total_acquiered_credits >= 60) {
                        self.bloc_result = {
                            'message' : _t("A validé 60 ECTS et est autorisé(e) à poursuivre son parcours sans restriction" ),
                            'class' : "success",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                        };
                    }
                    else if(self.bloc.total_acquiered_credits >= 45) {
                        self.bloc_result = {
                            'message' : _t("A validé au moins 45 ECTS et est autorisé à poursuivre son parcours tout en représentant les UE non validées."),
                            'class' : "warning",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                        };
                    } 
                    else if(self.bloc.total_acquiered_credits >= 30) {
                        self.bloc_result = {
                            'message' : _t("A validé au moins de 30 ECTS mais moins de 45. Peut compléter son programme ou non avec accord du jury."),
                            'class' : "danger",
                            'button_text' : _t("Échec"),
                            'next_action' : "failed",
                        };
                    } 
                    else {
                        self.bloc_result = {
                            'message' : _t("A validé moins de 30 ECTS. N’a pas rempli les conditions de réussite de son programme."),
                            'class' : "danger",
                            'button_text' : _t("Échec"),
                            'next_action' : "failed",
                        };
                    }
                    break;
                default :
                    self.bloc_result = {
                        'message' : _t("Cycle en cours." ),
                        'class' : "success",
                        'button_text' : _t("Réussite"),
                        'next_action' : "award",
                    };
            }
        }
    },
    
    _read_bloc_data: function(){
        var self = this;
        
        self.student_image = session.url('/web/image', {
            model: 'res.partner',
            id: self.bloc.student_id[0],
            field: 'image_medium',
            unique: (self.datarecord.__last_update || '').replace(/[^0-9]/g, '')
        });
        
        return rpc.query({
                    model: 'school.individual_course_group',
                    method: 'search_read',
                    domain: [['id', 'in', self.bloc.course_group_ids],['is_ghost_cg','=',false]],
                    fields: ['id','name','title','course_ids','dispense','final_result_bool','acquiered','first_session_computed_result','first_session_deliberated_result_bool','second_session_computed_result','second_session_deliberated_result_bool','second_session_result_bool','final_result','total_credits','total_weight'],
                }).then(
            function(course_groups) {
                self.course_groups = course_groups;
                var all_course_ids = [];
                self.course_group_id_map = {}
                for (var i=0, ii=self.course_groups.length; i<ii; i++) {
                    all_course_ids = all_course_ids.concat(self.course_groups[i].course_ids);
                    self.course_group_id_map[self.course_groups[i].id] = i;
                    self.course_groups[i].courses = [];
                }
                
                return rpc.query({
                    model: 'school.individual_course',
                    method: 'search_read',
                    domain: [['id', 'in', all_course_ids]],
                    fields: [],
                }).then(
                    function(courses) {
                        for (var i=0, ii=courses.length; i<ii; i++) {
                            var course = courses[i];
                            self.course_groups[self.course_group_id_map[course.course_group_id[0]]].courses.push(course);
                        }
                });
            }
        ).then(
            rpc.query({
                model: 'school.individual_program',
                method: 'search_read',
                domain: [['id','=',self.bloc.program_id[0]]],
                fields: [],
            }).then(
                function(program) {
                    if (program) {
                        self.program = program[0];
                        switch (self.program.grade) {
                          case "without":
                            self.program.grade_text = "sans grade";
                            break;
                          case "satisfaction":
                            self.program.grade_text = "avec Satisfaction";
                            break;
                          case "distinction":
                            self.program.grade_text = "avec Distinction";
                            break;
                          case "second_class":
                            self.program.grade_text = "avec la Grande Distinction";
                            break;
                          case "first_class":
                            self.program.grade_text = "avec la Plus Grande Distinction";
                            break;
                        };
                        rpc.query({
                            model: 'school.individual_program',
                            method: 'compute_evaluation_details',
                            args: [self.program.id],
                        }).then(function(results){
                            self.program.evaluation_details = results;
                        })
                    }
                    self._update_evaluation_messages();
                }
            )
        );
    },
});
});


                /*case "2" :
                    if(self.bloc.total_acquiered_credits >= 60) {
                        self.bloc_result = {
                            'message' : _t(self.bloc.total_acquiered_credits+" crédits ECTS acquis ou valorisés, autorisé(e) à poursuivre son parcours sans restriction." ),
                            'class' : "success",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                        };
                    }
                    else {
                        self.bloc_result = {
                            'message' : _t(self.bloc.total_acquiered_credits+" crédits ECTS acquis ou valorisés, autorisé(e) à poursuivre son parcours."),
                            'class' : "warning",
                            'button_text' : _t("Poursuite"),
                            'next_action' : "award",
                        };
                    }
                    break;
                case "3" :
                    if(self.bloc.total_acquiered_credits >= self.bloc.total_credits) {
                        self.bloc_result = {
                            'message' : _t("180 crédits ECTS acquis ou valorisés, le jury confère le grade académique de Bachelier avec "),
                            'class' : "success",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                        };
                        if(self.program.evaluation >= 18){
                            self.bloc_result.grade_text = _t("First Class Honor");
                            self.bloc_result.grade = 'first_class';
                        } else if (self.program.evaluation >= 16){
                            self.bloc_result.grade_text = _t("Second Class Honor");
                            self.bloc_result.grade = 'second_class';
                        } else if (self.program.evaluation >= 14){
                            self.bloc_result.grade_text = _t("Distinction");
                            self.bloc_result.grade = 'distinction';
                        } else if (self.program.evaluation >= 12){
                            self.bloc_result.grade_text = _t("Satisfaction");
                            self.bloc_result.grade = 'satisfaction';
                        } else {
                            self.bloc_result.grade_text = _t("Without Grade");
                            self.bloc_result.grade = 'without';
                        };
                    }
                    else if(self.bloc.total_credits - self.bloc.total_acquiered_credits <= 15) {
                        self.bloc_result = {
                            'message' : _t("Au moins 165 crédits ECTS acquis ou valorisés, autorisation d'accéder au programme de Master, les crédits résiduels devront être acquis avant toute délibération en Master."),
                            'class' : "success",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                        };
                    } 
                    else {
                        self.bloc_result = {
                            'message' : _t("Moins de 165 crédits ECTS acquis ou valorisés, pas de possibilité d'accéder au programme de Master."),
                            'class' : "danger",
                            'button_text' : _t("Échec"),
                            'next_action' : "failed",
                        };
                    }
                    break;
                    */
                    
                    
                                /*
            switch(self.bloc.source_bloc_level) {
                case "1" :
                    if(self.bloc.total_acquiered_credits >= self.bloc.total_credits) {
                        self.bloc_result = {
                            'message' : _t(self.bloc.total_acquiered_credits+" crédits ECTS acquis ou valorisés, autorisé(e) à poursuivre son parcours sans restriction." ),
                            'class' : "success",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                        };
                    }
                    else {
                        self.bloc_result = {
                            'message' : _t("Moins de "+self.bloc.total_credits+" crédits ECTS acquis ou valorisés, les crédits non-acquis sont à présenter, le cas échéant, en seconde session."),
                            'class' : "danger",
                            'button_text' : _t("Ajourné"),
                            'next_action' : "postpone",
                        };
                    }
                    break;
                case "2" :
                    if(self.bloc.total_acquiered_credits >= self.bloc.total_credits) {
                        self.bloc_result = {
                            'message' : _t(self.bloc.total_acquiered_credits+" crédits ECTS acquis ou valorisés, autorisé(e) à poursuivre son parcours sans restriction." ),
                            'class' : "success",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                        };
                    }
                    else {
                        self.bloc_result = {
                            'message' : _t("Moins de "+self.bloc.total_credits+" crédits ECTS acquis ou valorisés, les crédits non-acquis sont à présenter, le cas échéant, en seconde session."),
                            'class' : "danger",
                            'button_text' : _t("Ajourné"),
                            'next_action' : "postpone",
                        };
                    }
                    break;
                case "3" :
                    if(self.bloc.total_acquiered_credits >= self.bloc.total_credits) {
                        self.bloc_result = {
                            'message' : _t("180 crédits ECTS acquis ou valorisés, le jury confère le grade académique de Bachelier avec "),
                            'class' : "success",
                            'button_text' : _t("Réussite"),
                            'next_action' : "award",
                        };
                        if(self.program.evaluation >= 18){
                            self.bloc_result.grade_text = _t("First Class Honor");
                            self.bloc_result.grade = 'first_class';
                        } else if (self.program.evaluation >= 16){
                            self.bloc_result.grade_text = _t("Second Class Honor");
                            self.bloc_result.grade = 'second_class';
                        } else if (self.program.evaluation >= 14){
                            self.bloc_result.grade_text = _t("Distinction");
                            self.bloc_result.grade = 'distinction';
                        } else if (self.program.evaluation >= 12){
                            self.bloc_result.grade_text = _t("Satisfaction");
                            self.bloc_result.grade = 'satisfaction';
                        } else {
                            self.bloc_result.grade_text = _t("Without Grade");
                            self.bloc_result.grade = 'without';
                        };
                    }
                    else {
                        self.bloc_result = {
                            'message' : _t("Moins de "+self.bloc.total_credits+" crédits ECTS acquis ou valorisés, les crédits non-acquis sont à présenter, le cas échéant, en seconde session."),
                            'class' : "danger",
                            'button_text' : _t("Ajourné"),
                            'next_action' : "postpone",
                        };
                    }
                    break;
            }
            */