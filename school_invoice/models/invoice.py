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

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'

    invoice_id = fields.Many2one(
        'account.invoice', 'Invoice',
        copy=False, readonly=True, track_visibility="onchange")
        
    state = fields.Selection(selection_add=[('invoiced', 'Invoiced')])
    
    @api.multi
    def action_invoice_create(self):
        """ Creates invoice(s) for individual bloc.
        @return: Invoice Ids.
        """
        self.ensure_one()
        res = dict.fromkeys(self.ids, False)
        InvoiceLine = self.env['account.invoice.line']
        Invoice = self.env['account.invoice']
        invoice = False
        for bloc in self.filtered(lambda bloc: not bloc.invoice_id):
            invoice = Invoice.create({
                'name': bloc.name,
                'origin': bloc.name,
                'type': 'out_invoice',
                'partner_id': bloc.student_id.id,
                'date_invoice': "2016-09-15",
                
            })
            bloc.write({'invoiced': True, 'invoice_id': invoice.id})
            
            # if bloc.source_bloc_id.product_id:
            #     product = bloc.source_bloc_id.product_id
            #     invoice_line = InvoiceLine.create({
            #         'invoice_id': invoice.id,
            #         'name': product.name,
            #         'origin': bloc.name,
            #         'quantity': 1,
            #         'uom_id': product.uom.id,
            #         'price_unit': product.price_unit,
            #         'price_subtotal': product.uom_qty * product.price_unit,
            #         'product_id': product.id
            #     })
            # invoice.compute_taxes()
            res[bloc.id] = invoice.id
        if not invoice:
            invoice = self.invoice_id    
        self.write({
            'state' : 'invoiced',
        })
        return {
            'domain': [('id', 'in', res.values())],
            'name': 'Invoices',
            'res_id': invoice.id or self.invoice_id.id,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'view_id': False,
            'views': [(self.env.ref('account.invoice_form').id, 'form'),(self.env.ref('account.invoice_tree').id, 'tree')],
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window'
        }