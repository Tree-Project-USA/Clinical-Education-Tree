# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    max_distance_mel = fields.Float(string='Min Distance between zip codes (Mels)', default=100.0, required=True)
    max_hardship_zipcodes = fields.Integer(string='Number of Hardship ZipCodes', default=3)
    normal_number_zipcodes = fields.Integer(string='Number of Noraml ZipCodes', default=5, required=True)
    max_zipcodes_state = fields.Integer(string='Max ZipCodes in State', default=3, required=True)
    number_zipcodes_state = fields.Integer(string='Number of ZipCodes in State', default=3, required=True)
    clinical_distance_mel = fields.Float(string='Min Distance between Student and Site (Mels)', default=50.0, required=True)
    zip_code_token = fields.Char(string='Zip Code API Token')
    contract_notify_months = fields.Integer(string='Contract Notification Days', default=60, required=True)
    hardship_attachment = fields.Binary(string='Hardship Attachment')
