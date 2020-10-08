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
#
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

from collections import defaultdict

from openerp import api, fields, models, tools, _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class CreditAccount(models.Model):
    _name = 'school.credit.account'
    _inherit = ['mail.thread']
    _description = 'Credit Account'
    _order = 'code, name asc'

    code = fields.Char(string='Reference', index=True, tracking=True)
    name = fields.Char(string='Credit Account', index=True, required=True, tracking=True)
    active = fields.Boolean('Active', help="If the active field is set to False, it will allow you to hide the account without removing it.", default=True)
    
    line_ids = fields.One2many('school.credit.line', 'account_id', string="Credit Lines")
    
    balance = fields.Integer(compute='_compute_debit_credit_balance', string='Balance')
    debit = fields.Integer(compute='_compute_debit_credit_balance', string='Debit')
    credit = fields.Integer(compute='_compute_debit_credit_balance', string='Credit')
    
    @api.depends('line_ids.amount')
    def _compute_debit_credit_balance(self):

        analytic_line_obj = self.env['account.analytic.line']
        domain = [('account_id', 'in', self.ids)]
        if self._context.get('from_date', False):
            domain.append(('date', '>=', self._context['from_date']))
        if self._context.get('to_date', False):
            domain.append(('date', '<=', self._context['to_date']))

        credit_groups = analytic_line_obj.read_group(
            domain=domain + [('amount', '>=', 0.0)],
            fields=['account_id', 'amount'],
            groupby=['account_id'],
            lazy=False,
        )
        data_debit = defaultdict(credit_groups)

        debit_groups = analytic_line_obj.read_group(
            domain=domain + [('amount', '<', 0.0)],
            fields=['account_id', 'currency_id', 'amount'],
            groupby=['account_id', 'currency_id'],
            lazy=False,
        )
        data_debit = defaultdict(debit_groups)

        for account in self:
            account.debit = abs(data_debit.get(account.id, 0.0))
            account.credit = data_credit.get(account.id, 0.0)
            account.balance = account.credit - account.debit
    
class CreditLine(models.Model):
    _name = 'school.credit.line'
    _description = 'Analytic Line'
    _order = 'date desc, id desc'
    
    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    name = fields.Char('Description', required=True)
    date = fields.Date('Date', required=True, index=True, defult=fields.Date.context_today)
    amount = fields.Integer('Amount', required=True, default=0)
    account_id = fields.Many2one('school.credit.account', 'Credit Account', required=True, ondelete='restrict', index=True)
    pae_id = fields.Many2one('school.pae', 'PAE', required=True, ondelete='restrict')
    student_id = fields.Many2one('res.partner', string='Student', required=True, ondelete='restrict')
    individual_course_group_id = fields.Many2one('school.individual_course_group', 'Student Course Group', required=True, ondelete='restrict')
    individual_evaluation_id = fields.Many2one('school.individual_evaluation', 'Student Evaluation', ondelete='restrict')
    individual_valuation_id = fields.Many2one('school.individual_valuation', 'Course Group Valuation', ondelete='restrict')
    course_group_id = fields.Many2one('school.course_group', 'Course Group', required=True, ondelete='restrict')
    user_id = fields.Many2one('res.users', string='User', default=_default_user)
    