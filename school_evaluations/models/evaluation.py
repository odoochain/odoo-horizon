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
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

class CourseGroup(models.Model):
    '''Course Group'''
    _inherit = 'school.course_group'
    
    ## If set a course with an evaluation < 10 will make this course group not acquiered.
    # enable_exclusion_bool = fields.Boolean(string='Enable exclusion evaluation', default=False)
    
    def valuate_course_group(self):
        self.ensure_one()
        program_id = self.env.context.get('program_id')
        _logger.info('Add cg %s to %s' % (self.id, program_id))
        if program_id :
            program_id = self.env['school.individual_program'].browse(program_id)[0]
            cg = program_id.valuated_course_group_ids.create({
                'valuated_program_id' : program_id.id,
                'source_course_group_id': self.id, 
                'acquiered' : 'A',
                'course_ids': self.course_ids.ids,
                'state' : 'candidate',})
            program_id._get_total_acquiered_credits()
            return {
                'value' : {
                    'total_acquiered_credits' : program_id.total_acquiered_credits,
                    'total_registered_credits' : program_id.total_registered_credits,
                    'valuated_course_group_ids' : (6, 0, program_id.valuated_course_group_ids.ids)
                },
            }
    
class IndividualProgram(models.Model):
    '''Individual Program'''
    _inherit='school.individual_program'
    
    def set_to_abandonned(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'abandonned','abandonned_date':fields.Date.today()})
    
    historical_bloc_1_eval = fields.Float(string="Hist Bloc 1 Eval",track_visibility='onchange',digits=dp.get_precision('Evaluation'))
    historical_bloc_1_credits = fields.Integer(string="Hist Bloc 1 ECTS",track_visibility='onchange')
    
    historical_bloc_2_eval = fields.Float(string="Hist Bloc 2 Eval",track_visibility='onchange',digits=dp.get_precision('Evaluation'))
    historical_bloc_2_credits = fields.Integer(string="Hist Bloc 2 ECTS",track_visibility='onchange')
    
    grade = fields.Selection([
            ('without','Without Grade'),
            ('satisfaction','Satisfaction'),
            ('distinction','Distinction'),
            ('second_class', 'Second Class Honor'),
            ('first_class', 'First Class Honor'),
        ],string="Grade",track_visibility='onchange')
    
    grade_year_id = fields.Many2one('school.year', string="Graduation year",track_visibility='onchange')
    
    graduation_date = fields.Date(string="Graduation Date",track_visibility='onchange')
    
    grade_comments = fields.Text(string="Grade Comments",track_visibility='onchange')
    
    evaluation = fields.Float(string="Evaluation",compute="compute_evaluation",digits=dp.get_precision('Evaluation'),store=True)
    
    total_registered_credits = fields.Integer(compute='_get_total_acquiered_credits', string='Registered Credits',track_visibility='onchange',store=True)
    total_acquiered_credits = fields.Integer(compute='_get_total_acquiered_credits', string='Acquiered Credits', track_visibility='onchange',store=True)

    program_completed = fields.Boolean(compute='_get_total_acquiered_credits', string="Program Completed",track_visibility='onchange',store=True)

    valuated_course_group_ids = fields.One2many('school.individual_course_group', 'valuated_program_id', string='Valuated Courses Groups', track_visibility='onchange')

    @api.depends('valuated_course_group_ids', 'required_credits', 'bloc_ids.state','bloc_ids.total_acquiered_credits','historical_bloc_1_credits','historical_bloc_2_credits')
    def _get_total_acquiered_credits(self):
        for rec in self:
            _logger.debug('Trigger "_get_total_acquiered_credits" on Program %s' % rec.name)
            total = sum(cg.total_credits for cg in rec.valuated_course_group_ids) + sum(bloc_id.total_acquiered_credits if bloc_id.state in ['awarded_first_session','awarded_second_session','failed'] else 0 for bloc_id in rec.bloc_ids) or 0
            total_current = sum(bloc_id.total_credits if bloc_id.state in ['progress','postponed'] else 0 for bloc_id in rec.bloc_ids)
            rec.total_acquiered_credits = total + rec.historical_bloc_1_credits + rec.historical_bloc_2_credits
            rec.program_completed = rec.required_credits > 0 and rec.total_acquiered_credits >= rec.required_credits
            rec.total_registered_credits = rec.total_acquiered_credits + total_current
            rec.program_completed = rec.required_credits > 0 and rec.total_acquiered_credits >= rec.required_credits

    @api.depends('grade')
    def _onchange_grade(self):
        if self.grade:
            graduation_date = fields.Date.today()

    @api.depends('valuated_course_group_ids', 'bloc_ids.evaluation','historical_bloc_1_eval','historical_bloc_2_eval')
    def compute_evaluation(self):
        for rec in self:
            total = 0
            credit_count = 0
            for bloc in rec.bloc_ids:
                if bloc.evaluation > 0 : # if all is granted do not count
                    total += bloc.evaluation * bloc.total_credits
                    credit_count += bloc.total_credits
            if rec.historical_bloc_1_eval > 0:
                total += rec.historical_bloc_1_eval * rec.historical_bloc_1_credits
                credit_count += rec.historical_bloc_1_credits
            if rec.historical_bloc_2_eval > 0:
                total += rec.historical_bloc_2_eval * rec.historical_bloc_2_credits
                credit_count += rec.historical_bloc_2_credits
            if credit_count > 0:
                rec.evaluation = total/credit_count
        
    @api.depends('valuated_course_group_ids', 'bloc_ids.evaluation','historical_bloc_1_eval','historical_bloc_2_eval')
    def compute_evaluation_details(self):
        self.ensure_one();
        ret = [0,0,0,0,0,0]
        if self.historical_bloc_1_eval > 0:
            ret[0] = self.historical_bloc_1_eval
        if self.historical_bloc_2_eval > 0:
            ret[1] = self.historical_bloc_2_eval
        for bloc in self.bloc_ids:
            ret[int(bloc.source_bloc_level)-1] = bloc.evaluation
        return {
            'bloc_evaluations' : ret
        }
    
    all_ind_course_group_ids = fields.One2many('school.individual_course_group', string='All Courses Groups',compute='_compute_ind_course_group_ids_eval')
    not_acquired_ind_course_group_ids = fields.One2many('school.individual_course_group', string='Not Acquiered Courses Groups',compute='_compute_ind_course_group_ids_eval')
    acquired_ind_course_group_ids = fields.One2many('school.individual_course_group', string='Acquiered Courses Groups',compute='_compute_ind_course_group_ids_eval')
    remaining_course_group_ids  = fields.One2many('school.course_group', string='Remaining Courses Groups',compute='_compute_ind_course_group_ids_eval')
    remaining_not_planned_course_group_ids  = fields.One2many('school.course_group', string='Remaining and Not Planned Courses Groups',compute='_compute_ind_course_group_ids_eval')
    
    def _compute_ind_course_group_ids_eval(self):
        for rec in self:
            rec.all_ind_course_group_ids = rec.valuated_course_group_ids + rec.ind_course_group_ids
            rec.not_acquired_ind_course_group_ids = rec.ind_course_group_ids.filtered(lambda ic: ic.acquiered == 'NA')
            rec.acquired_ind_course_group_ids = rec.ind_course_group_ids.filtered(lambda ic: ic.acquiered == 'A') + rec.valuated_course_group_ids
            rec.remaining_course_group_ids = rec.source_program_id.course_group_ids - rec.acquired_ind_course_group_ids.mapped('source_course_group_id')
            if len(rec.bloc_ids) > 0 :
                rec.remaining_not_planned_course_group_ids = rec.remaining_course_group_ids - rec.bloc_ids[-1].course_group_ids.mapped('source_course_group_id')
            else :
                rec.remaining_not_planned_course_group_ids = rec.remaining_course_group_ids
                
class IndividualCourseSummary(models.Model):
    '''IndividualCourse Summary'''
    _inherit = 'school.individual_course_summary'
    
    def _compute_ind_course_group_ids(self):
        super(IndividualCourseSummary, self)._compute_ind_course_group_ids()
        for rec in self:
            rec.ind_course_group_ids |= rec.program_id.valuated_course_group_ids.filtered(lambda item: item.source_course_group_id.id == rec.course_group_id.id)
    
    state = fields.Selection([
            ('draft','Draft'),
            ('progress','In Progress'),
            ('confirmed', 'Confirmed'),
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('candidate','Candidate'),
            ('valuated', 'Valuated'),
        ], compute="_compute_state")
        
    trials = fields.Integer(string="Trials",compute='_compute_state')
        
    final_result_disp = fields.Char(string='Final Result Display', compute='_compute_state')
        
    def _compute_state(self):
        for rec in self:
            all_rec = rec.ind_course_group_ids
            rec.trials = len(all_rec)
            if len(all_rec) > 0 :
                rec.state = all_rec[-1].state
                rec.final_result_disp = all_rec[-1].final_result_disp
            else : 
                rec.state = 'draft'
                rec.final_result_disp = ""
                
class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'

    state = fields.Selection([
            ('draft','Draft'),
            ('progress','In Progress'),
            ('postponed', 'Postponed'),
            ('awarded_first_session', 'Awarded in First Session'),
            ('awarded_second_session', 'Awarded in Second Session'),
            ('failed', 'Failed'),
            ('abandoned','Abandoned'),
        ], string='Status', index=True, default='draft',
        copy=False,
        help=" * The 'Draft' status is used when results are not confirmed yet.\n"
             " * The 'In Progress' status is used during the courses.\n"
             " * The 'Postponed' status is used when a second session is required.\n"
             " * The 'Awarded' status is used when the bloc is awarded in either first or second session.\n"
             " * The 'Failed' status is used when the bloc is definitively considered as failed.\n"
             " * The 'Abandoned' status is when the student abandoned his bloc.\n"
             ,track_visibility='onchange')
    
    total_acquiered_credits = fields.Integer(compute="compute_credits",string="Acquiered Credits",store=True)
    total_acquiered_hours = fields.Integer(compute="compute_credits",string="Acquiered Hours",store=True)
    total_not_acquiered_credits = fields.Integer(compute='compute_credits', string='Not Acquiered Credits',store=True)
    total_not_acquiered_hours = fields.Integer(compute='compute_credits', string='Not Acquiered Hours',store=True)

    evaluation = fields.Float(string="Evaluation",compute="compute_evaluation",digits=dp.get_precision('Evaluation'),store=True)
    decision = fields.Text(string="Decision",track_visibility='onchange')
    exclude_from_deliberation = fields.Boolean(string='Exclude from Deliberation', default=False)
    
    first_session_result = fields.Float(string="Evaluation",compute="compute_evaluation",digits=dp.get_precision('Evaluation'),store=True)
    second_session_result = fields.Float(string="Evaluation",compute="compute_evaluation",digits=dp.get_precision('Evaluation'),store=True)
    
    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'draft' :
            self.course_group_ids.write({'state': 'draft'})
        elif self.state == 'progress' :
            self.course_group_ids.write({'state': 'progress'})
        elif self.state == 'postponed' :
            self.course_group_ids.write({'state': 'progress'})
        else :
            self.course_group_ids.write({'state': 'confirmed'})
    
    
    def set_to_draft(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        self.course_group_ids.write({'state': 'draft'})
        return self.write({'state': 'draft'})
    
    
    def set_to_progress(self, context):
        self.course_group_ids.write({'state': 'progress'})
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'progress'})
    
    def set_to_postponed(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            context = decision
            decision = None
        self._deliberate_cg(self.course_group_ids)
        return self.write({'state': 'postponed','decision' : decision})
    
    def set_to_awarded_first_session(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            context = decision
            decision = None
        self._deliberate_cg(self.course_group_ids)
        return self.write({'state': 'awarded_first_session','decision' : decision})
        
    def set_to_awarded_second_session(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            context = decision
            decision = None
        self._deliberate_cg(self.course_group_ids)
        return self.write({'state': 'awarded_second_session','decision' : decision})
    
    def set_to_failed(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            context = decision
            decision = None
        self._deliberate_cg(self.course_group_ids)
        return self.write({'state': 'failed','decision' : decision})
    
    def _deliberate_cg(self, cgs):
        for cg in cgs:
            if cg.acquiered :
                cg.write({'state': 'success'})
            else :
                cg.write({'state': 'failure'})
        pass
    
    def set_to_abandoned(self, decision=None, context=None):
        return self.write({'state': 'abandoned','decision' : None})
        
    def report_send(self):
        """ Open a window to compose an email, with the default template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('school_evaluations.email_template_success_certificate', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='school.individual_bloc',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        
    @api.depends('course_group_ids.total_credits','course_group_ids.total_hours','course_group_ids.acquiered','course_group_ids.first_session_computed_result_bool', 'course_group_ids.is_ghost_cg')
    def compute_credits(self):
        for rec in self:
            if rec.state in ['progress','postponed'] :
                rec.total_acquiered_credits = sum([icg.total_credits for icg in rec.course_group_ids if icg.acquiered == 'A' and not icg.is_ghost_cg])
                rec.total_acquiered_hours = sum([icg.total_hours for icg in rec.course_group_ids if icg.acquiered == 'A' and not icg.is_ghost_cg])
                rec.total_not_acquiered_credits = rec.total_credits - rec.total_acquiered_credits
                rec.total_not_acquiered_hours = rec.total_hours - rec.total_acquiered_hours
            else:
                # Don't compute if draft or finished
                pass

    @api.depends('course_group_ids.final_result','course_group_ids.total_weight','course_group_ids.acquiered', 'course_group_ids.is_ghost_cg')
    def compute_evaluation(self):
        for rec in self:
            if rec.state in ['progress','postponed'] :
                total = 0
                total_first = 0
                total_second = 0
                total_weight = 0
                for icg in rec.course_group_ids:
                    if icg.acquiered == 'A' :
                        total += icg.final_result * icg.total_weight
                        total_first += icg.first_session_result * icg.total_weight
                        total_second += icg.second_session_result * icg.total_weight
                        total_weight += icg.total_weight
                if total_weight > 0 :
                    rec.evaluation = total / total_weight
                    rec.first_session_result = total_first / total_weight
                    rec.second_session_result = total_second / total_weight
                else:
                    _logger.debug('total_weight is 0 on Bloc %s' % rec.name)
                    rec.evaluation = None
            else:
                # Don't compute if draft or finished
                pass
        
class IndividualCourseGroup(models.Model):
    '''Individual Course Group'''
    _inherit = 'school.individual_course_group'
    
    state = fields.Selection([
            ('9_draft','Draft'),
            ('7_failed', 'Failed'),
            ('6_success', 'Success'),
            ('5_progress','In Progress'),
            ('2_candidate','Candidate'),
            ('1_confirmed','Candidate'),
            ('0_valuated', 'Valuated'),
        ], string='Status', index=True, readonly=True, default='9_draft',
        track_visibility='onchange',
        copy=False,
        help=" * The 'Draft' status is used when course group is only plan.\n"
             " * The 'In Progress' status is used when results are not confirmed yet.\n"
             " * The 'Confirmed' status is when restults are confirmed.\n"
             " * The 'Success' status is when delibration has confirmed success.\n"
             " * The 'Failed' status is when delibration has confirmed failure.\n"
             " * The 'Candidate' status is used when the course group is candidate for valuation.\n"
             " * The 'Valuated' status is used when the course group is confirmed for valuation.")
        
    def set_to_confirmed(self, context):
        return self.write({'state': '1_confirmed'})
        
    def set_to_success(self, context):
        return self.write({'state': '6_success'})
        
    def set_to_failed(self, context):
        return self.write({'state': '7_failed'})
        
    def set_to_valuated(self, context):
        return self.write({'state': '0_valuated'})
    
    valuated_program_id = fields.Many2one('school.individual_program', string="Program", ondelete='cascade', readonly=True)
    
    @api.constrains('bloc_id','valuated_program_id')
    def _check_bloc_id_constrains(self):
        if self.bloc_id and self.valuated_program_id :
            raise UserError('A Course Group cannot be valuated in a program and in a bloc at the same time.')
    
    # Actions

    def valuate_course_group(self):
        self.ensure_one()
        program_id = self.bloc_id.program_id
        if program_id :
            self.write({
                'bloc_id' : False,
                'valuated_program_id' : program_id.id,
                'acquiered' : 'A',
                'state' : '2_candidate',})
            program_id._get_total_acquiered_credits()
            return {
                'value' : {
                    'total_acquiered_credits' : program_id.total_acquiered_credits,
                    'total_registered_credits' : program_id.total_registered_credits,
                    'valuated_course_group_ids' : (6, 0, program_id.valuated_course_group_ids.ids)
                },
            }
            
    def set_deliberated_to_ten(self, session = 1, message=''):
        for rec in self:
            if session == 1:
                rec.write({
                    'first_session_deliberated_result' : max(rec.first_session_computed_result, 10),
                    'first_session_deliberated_result_bool' : True,
                    'first_session_note': message,
                })
            else:
                rec.write({
                    'second_session_deliberated_result' : max(rec.second_session_computed_result, 10) if rec.second_session_computed_result_bool else max(rec.first_session_computed_result, 10),
                    'second_session_deliberated_result_bool' : True,
                    'second_session_note': message,
                })
    
    ## First Session ##
    
    first_session_computed_exception = fields.Selection(([('NP','NP'),('AB','AB'),('TP','TP')]),compute='compute_average_results',string='First Session Computed Exception', store=True)
    first_session_computed_result = fields.Float(compute='compute_average_results', string='First Session Computed Result', store=True, digits=dp.get_precision('Evaluation'))
    first_session_computed_result_bool= fields.Boolean(compute='compute_average_results', string='First Session Computed Active', store=True)

    first_session_deliberated_result = fields.Char(string='First Session Deliberated Result',track_visibility='onchange')
    first_session_deliberated_result_bool= fields.Boolean(string='First Session Deliberated Active',track_visibility='onchange')
    
    first_session_exception = fields.Selection(([('NP','NP'),('AB','AB'),('TP','TP')]),compute='compute_first_session_results',string='First Session Exception', store=True)
    first_session_result= fields.Float(compute='compute_first_session_results', string='First Session Result', store=True, digits=dp.get_precision('Evaluation'))
    first_session_result_bool= fields.Boolean(compute='compute_first_session_results', string='First Session Active', store=True)

    first_session_note = fields.Text(string='First Session Notes')
    
    ## Second Session ##
    
    second_session_computed_exception = fields.Selection(([('NP','NP'),('AB','AB'),('TP','TP')]),compute='compute_average_results',string='Second Session Computed Exception', store=True)
    second_session_computed_result = fields.Float(compute='compute_average_results', string='Second Session Computed Result', store=True,digits=dp.get_precision('Evaluation'))
    second_session_computed_result_bool= fields.Boolean(compute='compute_average_results', string='Second Session Computed Active', store=True)
    
    second_session_deliberated_result = fields.Char(string='Second Session Deliberated Result', digits=(5, 2),track_visibility='onchange')
    second_session_deliberated_result_bool= fields.Boolean(string='Second Session Deliberated Active',track_visibility='onchange')
    
    second_session_exception = fields.Selection(([('NP','NP'),('AB','AB'),('TP','TP')]),compute='compute_second_session_results',string='Second Session Exception', store=True)
    second_session_result= fields.Float(compute='compute_second_session_results', string='Second Session Result', store=True,digits=dp.get_precision('Evaluation'))
    second_session_result_bool= fields.Boolean(compute='compute_second_session_results', string='Second Session Active', store=True)
    
    second_session_note = fields.Text(string='Second Session Notes')
    
    ## Final ##
    
    final_result_exception = fields.Selection(([('NP','NP'),('AB','AB'),('TP','TP')]),compute='compute_final_results',string='Final Exception', store=True, track_visibility='onchange')
    final_result = fields.Float(compute='compute_final_results', string='Final Result', store=True, digits=dp.get_precision('Evaluation'), track_visibility='onchange')
    final_result_bool = fields.Boolean(compute='compute_final_results', string='Final Active', store=True)
    final_result_disp = fields.Char(string='Final Result Display', compute='compute_results_disp')
    
    acquiered = fields.Selection(([('A', 'Acquiered'),('NA', 'Not Acquiered')]), compute='compute_acquiered', string='Acquired Credits', store=True, track_visibility='onchange',default='NA')
    
    final_note = fields.Text(string='Final Notes')
    
    def compute_results_disp(self):
        for rec in self :
            if not rec.final_result_bool:
                rec.final_result_disp = ""
            elif rec.final_result_exception :
                rec.final_result_disp = rec.final_result_exception
            else :
                rec.final_result_disp = "%.2f" % rec.final_result
        
    def _parse_result(self,input):
        f = float(input)
        if(f < 0 or f > 20):
            raise ValidationError("Evaluation shall be between 0 and 20")
        else:
            return f
    
    @api.depends('course_ids.first_session_result_bool','course_ids.first_session_result','course_ids.first_session_exception','course_ids.second_session_result_bool','course_ids.second_session_result','course_ids.second_session_exception','course_ids.weight')
    def compute_average_results(self):
        for rec in self.filtered(lambda r: r.state in ['7_failed','5_progress']) :
            _logger.debug('Trigger "compute_average_results" on Course Group %s' % rec.name)
            ## Compute Weighted Average
            running_first_session_result = 0
            running_second_session_result = 0
            rec.first_session_computed_result_bool = False
            rec.second_session_computed_result_bool = False
            
            for ic in rec.course_ids:
                # Compute First Session 
                if ic.first_session_result_bool :
                    running_first_session_result += ic.first_session_result * ic.weight
                    rec.first_session_computed_result_bool = True
                # Compute Second Session
                if ic.second_session_result_bool :
                    if ic.second_session_result_bool :
                        running_second_session_result += ic.second_session_result * ic.weight
                    else :
                        running_second_session_result += ic.first_session_result * ic.weight
                    rec.second_session_computed_result_bool = True
                    
            if rec.first_session_computed_result_bool :
                if rec.total_weight > 0:
                    rec.first_session_computed_result = running_first_session_result / rec.total_weight
            if rec.second_session_computed_result_bool :
                if rec.total_weight > 0:
                    rec.second_session_computed_result = running_second_session_result / rec.total_weight
                    
            # for ic in rec.course_ids:
            #     if ic.first_session_exception :
            #         rec.first_session_computed_result = 0
            #         rec.first_session_computed_exception = ic.first_session_exception
            #         rec.first_session_computed_result_bool = True
            #         break
            
            # for ic in rec.course_ids:
            #     if ic.second_session_exception :
            #         rec.second_session_computed_result = 0
            #         rec.second_session_computed_exception = ic.first_session_exception
            #         rec.second_session_computed_result_bool = True
            #         break 
                    
            rec.compute_first_session_results()
            rec.compute_second_session_results()
        
    @api.depends('first_session_deliberated_result_bool','first_session_deliberated_result','first_session_computed_result_bool','first_session_computed_result','first_session_computed_exception')
    def compute_first_session_results(self):
        for rec in self.filtered(lambda r: r.state in ['7_failed','5_progress']) :
            _logger.debug('Trigger "compute_first_session_results" on Course Group %s' % rec.name)
            ## Compute Session Results
            if rec.first_session_deliberated_result_bool :
                try:
                    f = rec._parse_result(rec.first_session_deliberated_result)
                except ValueError:
                    rec.write('first_session_deliberated_result', None)
                    raise UserError(_('Cannot decode %s, please encode a Float eg "12.00".' % rec.first_session_deliberated_result))
                if (f < rec.first_session_computed_result):
                # TODO : take care of this - removed due to Cours artistiques B - Art dramatique - 2 - 2015-2016 - VALERIO Maddy 
                    raise ValidationError("Deliberated result must be above computed result, i.e. %s > %s in %s." % (rec.first_session_deliberated_result, rec.first_session_computed_result, rec.uid))
                else:
                    rec.first_session_exception = None
                    rec.first_session_result = f
                rec.first_session_result_bool = True
            elif rec.first_session_computed_exception :
                rec.first_session_exception = rec.first_session_computed_exception
                rec.first_session_result = 0
                rec.first_session_result_bool = True
            elif rec.first_session_computed_result_bool :
                rec.first_session_exception = None
                rec.first_session_result = rec.first_session_computed_result
                rec.first_session_result_bool = True
            else :
                rec.first_session_exception = None
                rec.first_session_result = 0
                rec.first_session_result_bool = False
            rec.compute_final_results()


    @api.depends('second_session_deliberated_result_bool','second_session_deliberated_result','second_session_computed_result_bool','second_session_computed_result','second_session_computed_exception')
    def compute_second_session_results(self):
        for rec in self.filtered(lambda r: r.state in ['7_failed','5_progress']) :
            _logger.debug('Trigger "compute_second_session_results" on Course Group %s' % rec.name)
            if rec.second_session_deliberated_result_bool :
                try:
                    f = rec._parse_result(rec.second_session_deliberated_result)
                except ValueError:
                    rec.write('second_session_deliberated_result', None)
                    raise UserError(_('Cannot decode %s, please encode a Float eg "12.00".' % rec.second_session_deliberated_result))
                if (f < rec.second_session_computed_result):
                    raise ValidationError("Deliberated result must be above computed result, i.e. %s > %s in %s." % (rec.second_session_deliberated_result, rec.second_session_computed_result, rec.uid))
                else:
                    rec.second_session_exception = None
                    rec.second_session_result = f
                rec.second_session_exception = None
                rec.second_session_result_bool = True
            elif rec.second_session_computed_exception :
                rec.second_session_exception = rec.first_session_computed_exception
                rec.second_session_result = 0
                rec.second_session_result_bool = True
            elif rec.second_session_computed_result_bool :
                rec.second_session_exception = None
                rec.second_session_result = rec.first_session_computed_result
                rec.second_session_result_bool = True
            else :
                rec.second_session_exception = None
                rec.second_session_result = 0
                rec.second_session_result_bool = False
            rec.compute_final_results()

    @api.depends('second_session_result_bool','second_session_exception','second_session_result','first_session_result_bool','first_session_exception','first_session_result')
    def compute_final_results(self):
        for rec in self.filtered(lambda r: r.state in ['7_failed','5_progress']) :
            _logger.debug('Trigger "compute_final_results" on Course Group %s' % rec.name)
            ## Compute Final Results
            if rec.second_session_result_bool :
                if rec.second_session_exception :
                    rec.final_result_exception = rec.second_session_exception
                    rec.final_result = 0
                    rec.final_result_bool = True
                else :
                    rec.final_result_exception = None
                    rec.final_result = rec.second_session_result
                    rec.final_result_bool = True
            elif rec.first_session_result_bool :
                if rec.first_session_exception :
                    rec.final_result_exception = rec.first_session_exception
                    rec.final_result = 0
                    rec.final_result_bool = True
                else :
                    rec.final_result_exception = None
                    rec.final_result = rec.first_session_result
                    rec.final_result_bool = True
            else :
                rec.final_result_exception = None
                rec.final_result = 0
                rec.final_result_bool = False
            if rec.final_result >= 10 : 
                rec.acquiered = 'A'

class IndividualCourse(models.Model):
    '''Individual Course'''
    _inherit = 'school.individual_course'
    
    type = fields.Selection(([('S', 'Simple'),('C', 'Complex'),('D','Deferred')]),string='Type', readonly=True) # Kept for archiving purpose
    
    ann_result= fields.Char(string='Annual Result',readonly=True) # Kept for archiving purpose
    jan_result= fields.Char(string='January Result',readonly=True) # Kept for archiving purpose
    jun_result= fields.Char(string='June Result',readonly=True) # Kept for archiving purpose
    sept_result= fields.Char(string='September Result',readonly=True) # Kept for archiving purpose
    
    partial_result = fields.Char(string='Partial Result',track_visibility='onchange')
    final_result = fields.Char(string='Final Result',track_visibility='onchange')
    second_result = fields.Char(string='Second Result',track_visibility='onchange')
    
    is_annual = fields.Boolean(string="Is Annual", related='source_course_id.is_annual',readonly=True)
    
    ## First Session ##
    
    first_session_exception = fields.Selection(([('NP','NP'),('AB','AB'),('TP','TP')]),compute='compute_results',string='First Session Exception', store=True)
    first_session_result = fields.Float(compute='compute_results', string='First Session Result', store=True, group_operator='avg',digits=dp.get_precision('Evaluation'))
    first_session_result_bool = fields.Boolean(compute='compute_results', string='First Session Active', store=True)
    first_session_note = fields.Text(string='First Session Notes')

    ## Second Session ##
    
    second_session_exception = fields.Selection(([('NP','NP'),('AB','AB'),('TP','TP')]),compute='compute_results',string='Second Session Exception', store=True)
    second_session_result= fields.Float(compute='compute_results', string='Second Session Result', store=True, group_operator='avg', digits=dp.get_precision('Evaluation'))
    second_session_result_bool = fields.Boolean(compute='compute_results', string='Second Session Active', store=True)
    second_session_note = fields.Text(string='Second Session Notes')

    is_danger = fields.Boolean(compute="compute_results", store=True)

    @api.depends('partial_result','final_result','second_result')
    def compute_results(self):
        for rec in self.filtered(lambda r: r.course_group_id.state in ['7_failed','5_progress']) :
            if rec.partial_result :
                try:
                    if rec.partial_result == "NP":
                        pass
                    elif rec.partial_result == "AB":
                        pass
                    elif rec.partial_result == "TP":
                        pass
                    else :
                        f = float(rec.partial_result)
                        rec.partial_result = format(f,".2f")
                        if(f < 0 or f > 20):
                            raise ValidationError("Evaluation shall be between 0 and 20")
                        else:
                            pass
                except ValueError:
                    raise UserError(_('Cannot decode %s in June Result, please encode a Float eg "12.00" or "NP" or "AB" or "TP".' % rec.partial_result))
                    
            if rec.final_result :
                try:
                    if rec.final_result == "NP":
                        rec.first_session_result = 0
                        rec.first_session_exception = 'NP'
                        rec.first_session_result_bool = True
                        rec.is_danger = True
                    elif rec.final_result == "AB":
                        rec.first_session_result = 0
                        rec.first_session_exception = 'AB'
                        rec.first_session_result_bool = True
                        rec.is_danger = True
                    elif rec.final_result == "TP":
                        rec.first_session_result = 0
                        rec.first_session_exception = 'TP'
                        rec.first_session_result_bool = True
                        rec.is_danger = True
                    else :
                        f = float(rec.final_result)
                        if(f < 0 or f > 20):
                            raise ValidationError("Evaluation shall be between 0 and 20")
                        else:
                            rec.final_result = format(f,".2f")
                            rec.first_session_result = f
                            rec.first_session_exception = None
                            rec.first_session_result_bool = True
                            if f < 10 :
                                rec.is_danger = True
                            else:
                                rec.is_danger = False
                except ValueError:
                    rec.first_session_result = 0
                    rec.first_session_exception = None
                    rec.first_session_result_bool = False
                    raise UserError(_('Cannot decode %s in June Result, please encode a Float eg "12.00" or "NP" or "AB" or "TP".' % rec.jun_result))

            if rec.second_result :
                try:
                    if rec.second_result == "NP":
                        rec.second_session_exception = 'NP'
                        rec.second_session_result = 0
                        rec.second_session_result_bool = True
                        rec.is_danger = True
                    elif rec.second_result == "AB":
                        rec.second_session_exception = 'AB'
                        rec.second_session_result = 0
                        rec.second_session_result_bool = True
                        rec.is_danger = True
                    elif rec.second_result == "TP":
                        rec.second_session_exception = 'TP'
                        rec.second_session_result = 0
                        rec.second_session_result_bool = True
                        rec.is_danger = True
                    else :
                        f = float(rec.second_result)
                        if(f < 0 or f > 20):
                            raise ValidationError("Evaluation shall be between 0 and 20")
                        else:
                            rec.second_result = format(f,".2f")
                            rec.second_session_result = f
                            rec.second_session_exception = None
                            rec.second_session_result_bool = True
                            if f < 10 :
                                rec.is_danger = True
                            else:
                                rec.is_danger = False
                except ValueError:
                    rec.second_session_result = 0
                    rec.second_session_exception = None
                    rec.second_session_result_bool = False
                    raise UserError(_('Cannot decode %s in September Result, please encode a Float eg "12.00" or "NP" or "AB" or "TP".' % rec.sept_result))