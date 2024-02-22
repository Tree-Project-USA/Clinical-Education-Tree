# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    max_distance_mel = fields.Float(string='Max Distance Mels', default=100.0, required=True)
    max_hardship_zipcodes = fields.Integer(string='Max Hardship ZipCodes', default=0)
    normal_number_zipcodes = fields.Integer(string='Noraml Hardship ZipCodes', default=5, required=True)
    max_zipcodes_state = fields.Integer(string='Max ZipCodes in State', default=3, required=True)
    clinical_distance_mel = fields.Float(string='Max Distance Mels', default=50.0, required=True)
    zip_code_token = fields.Char(string='Zip Code API Token')
    contract_notify_months = fields.Integer(string='Contract Notification Days', default=60, required=True)
    hardship_attachment = fields.Binary(required=True)
