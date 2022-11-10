import logging

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    '''Partner'''
    _name = 'res.partner'
    _inherit = ['res.partner', 'google_drive_folder']