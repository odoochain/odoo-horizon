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
import io
from datetime import datetime, timedelta

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
    def _getCertificate(self):
        res_company = self.env['res.company'].browse(self.env.context['allowed_company_ids'][0])
        return {
            'webservices_key': io.BytesIO(res_company.webservices_key).get_value(),
            'webservices_key_passwd': res_company.webservices_key_passwd,
            'webservices_certificate': io.BytesIO(res_company.webservices_certificate).get_value(),
        }

    @api.model
    def _getClient(self):
        if not self._soapClientsCache.get(self.name):
            cert = self._getCertificate()
            try:
                from zeep.transports import Transport
                transport = Transport(timeout=TIMEOUT)
                from zeep import CachingClient
                from zeep.wsse.signature import MemorySignature
                client = CachingClient(self.wsdl_url, transport=transport,
                    wsse=MemorySignature(cert['webservices_key'], cert['webservices_certificate'], cert['webservices_key_passwd']))
            except ImportError:
                # fall back to non-caching zeep client
                try:
                    from zeep import Client
                    from zeep.wsse.signature import MemorySignature
                    client = Client(self.wsdl_url, transport=transport,
                    wsse=MemorySignature(cert['webservices_key'], cert['webservices_certificate'], cert['webservices_key_passwd']))
                except ImportError:
                    raise ImportError('Pleas install zeep SOAP Library')
            self._soapClientsCache[self.name] = client
        return self._soapClientsCache[self.name]

    name = fields.Char('name')
    wsdl_url = fields.Char('WSDL Url')

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

    def action_test_service(self):
        self.doRequest(self.env.context['allowed_company_ids'][0])

    def __callOperation(self, client, record=False):
        if self.name == 'fase':
            message = {
                'soapenv:Envelope': {
                    '@xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                    'soapenv:Header': {
                        '@xmlns:wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
                        'wsse:Security': {
                            '@mustUnderstand': 'true',
                            '@xmlns:wsu': 'http://schemas.xmlsoap.org/ws/2002/07/utility',
                            'wsu:Timestamp': {
                                'wsu:Created': datetime.utcnow().isoformat() + 'Z',
                                'wsu:Expires': (datetime.utcnow() + timedelta(minutes=5)).isoformat() + 'Z',
                            }
                        },
                        '@xmlns:wsa': 'http://www.w3.org/2005/08/addressing',
                        'wsa:Action': 'domaine:fase?mode=sync',
                        'wsa:From': {
                            'wsa:Address': 'https://horizon.student-crlg.be'
                        },
                        'wsa:MessageID': 'uuid:3164ab7f-bf5a-423b-95ba-f4e5ebddd6b0',
                        'wsa:To': 'http://www.etnic.be/janus/dedale'
                    },
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
