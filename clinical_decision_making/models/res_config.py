# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import ast


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
        string='Max Distance Mels', default=50.0,
        config_parameter='clinical_distance_mel')
    zip_code_token = fields.Char(
        string='Zip Code API Token',
        config_parameter='zip_code_token')
    contract_notify_months = fields.Integer(
        string='Contract Notification Days',
        config_parameter='contract_notify_months')
    hardship_attachment = fields.Binary(
        related='company_id.hardship_form_attachment',
        readonly=False
    )
    
    @api.model
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('clinical_decision_making.hardship_attachment', self.hardship_attachment)
        return res
    
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            hardship_attachment = self.env['ir.config_parameter'].sudo().get_param('clinical_decision_making.hardship_attachment')
        )
        return res
