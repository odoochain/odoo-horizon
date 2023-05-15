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
import io
from datetime import datetime, timedelta
import uuid
from lxml import etree

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from zeep.transports import Transport
from zeep import CachingClient
from zeep.wsse.signature import MemorySignature
import os
from zeep.plugins import HistoryPlugin

_logger = logging.getLogger(__name__)

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

_history = HistoryPlugin()

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
            'webservices_key': io.BytesIO(base64.decodebytes(res_company.webservices_key)).read().decode('utf-8'),
            'webservices_key_passwd': res_company.webservices_key_passwd,
            'webservices_certificate': io.BytesIO(base64.decodebytes(res_company.webservices_certificate)).read().decode('utf-8'),
        }

    @api.model
    def _getClient(self):
        if not self._soapClientsCache.get(self.name):
            cert = self._getCertificate()
            transport = Transport(timeout=TIMEOUT)
            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, '../static' + self.wsdl_url)
            client = CachingClient(filename, transport=transport,
                wsse=MemorySignature(cert['webservices_key'], cert['webservices_certificate'], cert['webservices_key_passwd']), plugins=[_history])
            self._soapClientsCache[self.name] = client
        return self._soapClientsCache[self.name]

    name = fields.Char('name')
    wsdl_url = fields.Char('WSDL Url')
    wsa_action = fields.Char('Action WS-Addressing')
    wsa_to = fields.Char('Destination (To) WS-Addressing')

    def doRequest(self, record=False):
        self.ensure_one()
        client = self._getClient()
        result = self._callOperation(client, record)
        self._applyChanges(result, record)

    def _callOperation(self, record=False):
        raise NotImplementedError('__callOperation not implemted for service %s' % self.name)

    def _applyChanges(self, record=False):
        raise NotImplementedError('_applyChanges not implemted for service %s' % self.name)

    def action_test_service(self):
        raise NotImplementedError('action_test_service not implemted for service %s' % self.name)

    def _get_Headers(self):
        return self._get_WSA_Headers() + self._get_WSSE_Headers()

    def _get_WSA_Headers(self):
        # Create the wsa:Action element
        wsa_action = etree.Element("{http://www.w3.org/2005/08/addressing}Action")
        wsa_action.text = self.wsa_action

        # Create the wsa:From element
        wsa_from = etree.Element("{http://www.w3.org/2005/08/addressing}From")
        wsa_address = etree.Element("{http://www.w3.org/2005/08/addressing}Address")
        wsa_address.text = self.wsa_to
        wsa_from.append(wsa_address)

        # Create the wsa:MessageID element
        wsa_message_id = etree.Element("{http://www.w3.org/2005/08/addressing}MessageID")
        wsa_message_id.text = 'uuid:%s' % uuid.uuid4()

        # Create the wsa:To element
        wsa_to = etree.Element("{http://www.w3.org/2005/08/addressing}To")
        wsa_to.text = "http://www.etnic.be/services/fase"

        return [wsa_action, wsa_from, wsa_message_id, wsa_to]

    def _get_WSSE_Headers(self):
        return []
    #     timestamp = datetime.now()
    #     expires = timestamp + timedelta(minutes=10)

    #     wsse_security = etree.Element("{http://docs.oasisopen.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Security")
    #     wsse_security.set("{http://www.w3.org/2003/05/soap-envelope}mustUnderstand", "1")

    #     wsu_timestamp = etree.Element("{http://docs.oasisopen.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Timestamp")
    #     wsu_timestamp.set("{http://docs.oasisopen.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id", 'id-%s' % uuid.uuid4())

    #     wsu_created = etree.Element("{http://docs.oasisopen.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Created")
    #     wsu_created.text = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    #     wsu_expires = etree.Element("{http://docs.oasisopen.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Expires")
    #     wsu_expires.text = expires.strftime("%Y-%m-%dT%H:%M:%SZ")
    #     wsu_timestamp.append(wsu_created)
    #     wsu_timestamp.append(wsu_expires)

    #     wsse_security.append(wsu_timestamp)

    #     return [wsse_security]

class FaseService(models.Model):
    '''Fase Web Service'''
    _inherit = 'school.webservice'

    def action_test_service(self):
        if self.name == 'fase':
            resp = self.doRequest(self.env['res.company'].browse(self.env.context['allowed_company_ids'][0]))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Web Service response : %s' % etree.tostring(_history.last_received["envelope"], encoding="unicode", pretty_print=True)),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'warning',
                }
            }
        else:
            self.super()

    def _callOperation(self, client, record=False):
        if self.name == 'fase':
            fase_ns = 'http://www.etnic.be/services/fase/organisation/v2'
            fase_cfwb_ns = 'http://www.cfwb.be/enseignement/fase'
            fase = client.type_factory(fase_ns)
            fase_cfwb = client.type_factory(fase_cfwb_ns)
            res = client.service.obtenirOrganisation(
                Organisation=[fase.OrganisationCT(
                    Type=fase_cfwb.OrganisationST('ETAB'),
                    Identifiant=2066
                )],Dmd=fase_cfwb.DmdST('FICHE'), _soapheaders=self._get_Headers())
            _logger.info('FASE Response : %s' % res)
        else:
            self.super(client, record)

    def _applyChanges(self, result, record=False):
        if self.name == 'fase':
            _logger.info('FASE Info : %s' % result)
        else:
            self.super(result, record)
