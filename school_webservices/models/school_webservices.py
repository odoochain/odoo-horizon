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

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

TIMEOUT = 30

class WebService(models.Model):
    '''Web Service'''
    _name = 'school.webservice'
    _description = 'Web Service'

    _soapClientsCache = {}

    @api.model
    def refreshClients(self):
        self._soapClientsCache = {}

    @api.model
    def _getClient(self):
        if not self._soapClientsCache[self.name]:
            try:
                from zeep.transports import Transport
                transport = Transport(timeout=TIMEOUT)
                from zeep import CachingClient
                client = CachingClient(self.wsdl_url, transport=transport).service
            except ImportError:
                # fall back to non-caching zeep client
                try:
                    from zeep import Client
                    client = Client(self.wsdl_url, transport=transport).service
                except ImportError:
                    raise ImportError('Pleas install zeep SOAP Library')
            self._soapClientsCache[self.name] = client
        return self._soapClientsCache[self.name]

    name = fields.String('name')
    wsdl_url = fields.String('WSDL Url')

    def doRequest(self, record=False):
        self.ensure_one()
        client = self._getClient()
        result = self._callOperation(client, record)
        self._applyChanges(result, record)

    def __callOperation(self, record=False):
        raise NotImplementedError('__callOperation not implemted for service %s' % self.name)

    def _applyChanges(self, record=False):
        raise NotImplementedError('_applyChanges not implemted for service %s' % self.name)

class FaseService(models.Model):
    '''Fase Web Service'''
    _inherit = 'school.webservice'

    def __callOperation(self, client, record=False):
        if self.name == 'fase':
            message = {
                'soapenv:Envelope': {
                    '@xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                    'soapenv:Header': {},
                    'soapenv:Body': {
                        'fase:ObtenirOrganisationRequete': {
                            '@xmlns:fase': 'http://www.etnic.be/services/fase/organisation/v2',
                            'fase:Organisation': {
                                'fase:Type': 'ETAB',
                                'fase:Identifiant': record.fase_code
                            },
                            'fase:Dmd': 'FICHE'
                        }
                    }
                }
            }
            return client.service.obtenirOrganisation(message)
        else:
            self.super(client, record)

    def _applyChanges(self, result, record=False):
        if self.name == 'fase':
            _logger.info('FASE Info : %s' % result)
        else:
            self.super(result, record)
