# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    max_distance_mel = fields.Float(
        string='Max Distance Mels', default=100.0,
        config_parameter='max_distance_mel')
    max_hardship_zipcodes = fields.Integer(
        string='Max Hardship ZipCodes', default=0,
        config_parameter='max_hardship_zipcodes')
    normal_number_zipcodes = fields.Integer(
        string='Noraml Hardship ZipCodes', default=0,
        config_parameter='normal_number_zipcodes')
    max_zipcodes_state = fields.Integer(
        string='Max ZipCodes in State', default=0,
        config_parameter='max_zipcodes_in_state')
    clinical_distance_mel = fields.Float(
        string='Max Distance Mels', default=75.0,
        config_parameter='clinical_distance_mel')
    zip_code_token = fields.Char(
        string='Zip Code API Token',
        config_parameter='zip_code_token')
