# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2023 ito-invest.lu
#                       Jerome Sonnet <jerome.sonnet@ito-invest.lu>
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
import logging.config
import base64
import os
import io
from datetime import datetime, timedelta
import uuid
from lxml import etree

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class PersonService(models.Model):
    _inherit = 'school.webservice'

    def getWSLDFile(self):
        dirname = os.path.dirname(__file__)
        return os.path.join(dirname, '../static' + self.wsdl_url)

    def action_test_service(self):
        _logger.info('PersonService action_test_service')
        if self.name == 'bced_personne':
            resp = self.doRequest(self.env.user)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Web Service response : %s' % resp),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'warning',
                }
            }
        else:
            return super().action_test_service()
    
    def _callOperation(self, client, record=False):
        if self.name == 'bced_personne':
            # create the types
            person_ns = "http://soa.spw.wallonie.be/services/person/messages/v3"
            id_ns = "http://soa.spw.wallonie.be/common/identification/v1"
            priv_ns = "http://soa.spw.wallonie.be/common/privacylog/v1"

            person = client.type_factory(person_ns)
            id = client.type_factory(id_ns)
            priv = client.type_factory(priv_ns)

            res = client.service.getPerson(
                customerInformations=[id.CustomerInformationType(
                    ticket=uuid.uuid4(),
                    timestampSent=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    customerIdentification={
                        'organisationId' : self.env['res.company'].browse(self.env.context['allowed_company_ids'][0]).fase_code
                    }
                )],
                privacyLog={
                    'context' : 'HIGH_SCHOOL_CAREER',
                    'treatmentManagerIdentifier' : {
                        '_value_1' : self.env.user.national_id,
                        'identityManager' : 'RN/RBis'
                    },
                    'dossier' : {
                        'dossierId' : {
                            # TODO : what are the information to provide here ?
                            '_value_1' : '0',
                            'source' : 'CRLg'
                        }
                    }
                },
                request={
                    'personNumber' : record.national_id
                }
            )
            return res
        else:
            return super()._callOperation(client, record)

    def _applyChanges(self, result, record=False):
        if self.name == 'fase':
            _logger.info('FASE Info : %s' % result)
        else:
            super(result, record)
