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


class BCEDInscription(models.Model):
    _inherit = 'school.webservice'

    def action_test_service(self):
        if self.name == 'bced_inscription':
            _logger.info('PersonService action_test_service')
            client = self._getClient()

            priv_ns = "http://bced.wallonie.be/common/privacylog/v5"

            priv = client.type_factory(priv_ns)

            if not self.env.user.national_id:
                raise UserError(_('You must have a national id on current user to test this service'))

            # Create the request objects
            res = client.service.closeInscription(
                requestIdentification={
                    'ticket' : 'edd90daf-a72f-4585-acee-0f9da279f8d0',
                    'timestampSent' : datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                privacyLog=priv.PrivacyLogType(
                    context='HIGH_SCHOOL_CAREER',
                    treatmentManagerNumber=self.env.user.national_id,
                    dossier={
                        'dossierId' : {
                            # TODO : what are the information to provide here ?
                            '_value_1' : '0',
                            'source' : 'CRLg'
                        }
                    }
                ),
                request={
                    'inscription' : {
                        'personNumber' : '00010226601',
                        'period' : {
                            'beginDate' : datetime.now().strftime("%Y-%m-%d")
                        }
                    }
                }
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Web Service response : %s' % res),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'warning',
                }
            }
        else:
            return super().action_test_service()

    def publishInscription(self, inscription):
        client = self._getClient()
        if inscription :
            # create the types
            priv_ns = "http://bced.wallonie.be/common/privacylog/v5"

            priv = client.type_factory(priv_ns)

            if not self.env.user.national_id:
                raise UserError(_('You must have a national id on current user to test this service'))

            # Create the request objects
            res = client.service.publishInscription(
                requestIdentification={
                    'ticket' : uuid.uuid4(),
                    'timestampSent' : datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                privacyLog=priv.PrivacyLogType(
                    context='HIGH_SCHOOL_CAREER',
                    treatmentManagerNumber=self.env.user.national_id,
                    dossier={
                        'dossierId' : {
                            # TODO : what are the information to provide here ?
                            '_value_1' : '0',
                            'source' : 'CRLg'
                        }
                    }
                ),
                request={
                    'personNumber' : inscription.partner_id.reg_number,
                    'period' : {
                        'beginDate' : inscription.start_date.strftime("%Y-%m-%d")
                    }
                }
            )
            if res['error']:
                if res['error']['cause']:
                    raise UserError(_('Error while publishing inscription with code %s : %s ' % (res['error']['code'],res['error']['cause'])))
                else:
                    raise UserError(_('Error while publishing inscription with code %s' % res['error']['code']))
            return res
        else:
            raise UserError(_('You must provide an inscription to publish'))

class PersonService(models.Model):
    _inherit = 'school.webservice'

    def action_test_service(self):
        if self.name == 'bced_personne':
            _logger.info('PersonService action_test_service')

            client = self._getClient()

            person_ns = "http://soa.spw.wallonie.be/services/person/messages/v3"
            id_ns = "http://soa.spw.wallonie.be/common/identification/v1"
            priv_ns = "http://soa.spw.wallonie.be/common/privacylog/v1"

            person = client.type_factory(person_ns)
            id = client.type_factory(id_ns)
            priv = client.type_factory(priv_ns)

            if not self.env.user.national_id:
                raise UserError(_('You must have a national id on current user to test this service'))

            if not self.env.user.company_id.fase_code:
                raise UserError(_('You must have a fase code on current company to test this service'))

            res = client.service.getPerson(
                customerInformations=[id.CustomerInformationType(
                    ticket=uuid.uuid4(),
                    timestampSent=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    customerIdentification={
                        'organisationId' : self.env.user.company_id.fase_code
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
                    'personNumber' : self.env.user.national_id,
                }
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Web Service response : %s' % res),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,
                    'type': 'warning',
                }
            }
        else:
            return super().action_test_service()

    def searchPersonByName(self, partner_id):
        client = self._getClient()
        if partner_id :
            # create the types
            person_ns = "http://soa.spw.wallonie.be/services/person/messages/v3"
            id_ns = "http://soa.spw.wallonie.be/common/identification/v1"
            priv_ns = "http://soa.spw.wallonie.be/common/privacylog/v1"

            person = client.type_factory(person_ns)
            id = client.type_factory(id_ns)
            priv = client.type_factory(priv_ns)

            if not partner_id.lastname:
                raise UserError(_('You must have a lastname on the partner to search for a person'))

            if not partner_id.birthdate_date:
                raise UserError(_('You must have a birthdate on the partner to search for a person'))

            res = client.service.searchPersonByName(
                customerInformations=[id.CustomerInformationType(
                    ticket=uuid.uuid4(),
                    timestampSent=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    customerIdentification={
                        'organisationId' : self.env.user.company_id.fase_code
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
                    'personName' :{
                        'lastName' : partner_id.lastname,
                    },
                    'birthDate' : partner_id.birthdate_date.strftime("%Y-%m-%d"),
                    'birthDateTolerance' : 0,
                }
            )
            return res
        else:
            raise ValidationError(_('No partner provided'))
    
    def getPerson(self, reference):
        client = self._getClient()
        if reference :
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
                        'organisationId' : self.env.user.company_id.fase_code
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
                    'personNumber' : reference,
                }
            )
            if res['status']['code'] != 'SOA0000000':
                raise ValidationError(_('Error while getting person : %s' % res['status']))
            return res['person']
        else:
            raise ValidationError(_('No record provided'))

    def publishPerson(self, partner_id):
        client = self._getClient()
        if partner_id :
            # create the types
            person_ns = "http://soa.spw.wallonie.be/services/person/messages/v3"
            id_ns = "http://soa.spw.wallonie.be/common/identification/v1"
            priv_ns = "http://soa.spw.wallonie.be/common/privacylog/v1"

            person = client.type_factory(person_ns)
            id = client.type_factory(id_ns)
            priv = client.type_factory(priv_ns)

            # We make the choice to ask at least for the firstname, lastname and birthdate to get a bis number
            if not partner_id.firstname:
                raise UserError(_('You must have a firstname on the partner to get a bis number'))
            if not partner_id.lastname:
                raise UserError(_('You must have a lastname on the partner to get a bis number'))
            if not partner_id.birthdate_date:
                raise UserError(_('You must have a birthdate on the partner to get a bis number'))

            inceptionDate = partner_id.birthdate_date.strftime("%Y-%m-%d")

            res = client.service.publishPerson(
                customerInformations=[id.CustomerInformationType(
                    ticket=uuid.uuid4(),
                    timestampSent=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    customerIdentification={
                        'organisationId' : self.env.user.company_id.fase_code
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
                    'person' : {
                        'register':'Bis',
                        'name' :{
                            'inceptionDate' : inceptionDate,
                            'fisrtName' : {
                                'sequence' : 1,
                                '_value_1' : partner_id.firstname,
                            },
                            'lastName' : partner_id.lastname,
                        },
                        'gender': {
                            'inceptionDate' : inceptionDate,
                            'code': 'M' if partner_id.gender == 'male' else 'F',
                        } if partner_id.gender else None,
                        'nationalities':{
                            'nationality': [
                                [{
                                    'inceptionDate' : inceptionDate,
                                    'code' : c.nis_code
                                } for c in partner_id.nationality_ids]
                            ]
                        } if partner_id.nationality_ids else None,
                        'birth':{
                            'officialBirthDate' : inceptionDate,
                            'birthPlace' : {
                                'country' : {
                                    'code' : partner_id.birthcountry.nis_code,
                                } if partner_id.birthcountry else None,
                                'municipality' : {
                                    'description' : partner_id.birthplace,
                                } if partner_id.birthcountry else None,
                            }
                        },
                    }
                }
            )
            if res['status']['code'] != 'SOA0000000':
                raise ValidationError(_('Error while publishing person : %s' % res['status']))
            return res['result']['personNumber']
        else:
            raise ValidationError(_('No partner provided'))
