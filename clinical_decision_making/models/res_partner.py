# -*- coding: utf-8 -*-
import requests
import json
from odoo import models, fields, api, _
from odoo.addons.clinical_decision_making.models.setting import get_distance
from odoo.exceptions import ValidationError

class NamaModel(models.Model):
    _inherit = 'res.partner'
    
    is_student = fields.Boolean(string='Is Student', default=False)
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    cohort_label = fields.Char(string='Cohort Label')
    graduation_date = fields.Date(string='Graduation Date', required=True)
    home_address = fields.Char(string='Home Address')
    setting_ids = fields.Many2many(comodel_name='category.setting', string='Category Setting')
    locatio_ids = fields.One2many(comodel_name='location.setting', inverse_name='student_id', string='Locations')
    can_apply_hardship = fields.Boolean(string='Apply Hardship', default=False)
    is_reach_maximum_zip_code = fields.Boolean(string='Reach Maximum Zip Code', default=False)

    @api.onchange('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.first_name if rec.first_name else '' + ', ' + rec.last_name if rec.last_name else ''
    
    def check_zip_code_distance(self, list_code):
        max_distance_mel = self.env['ir.config_parameter'].sudo(
        ).get_param('max_distance_mel')
        for zip_code in list_code:
            for single_code in list_code:
                if zip_code != single_code:
                    distance = get_distance(zip_code, single_code)
                    if distance and distance < float(max_distance_mel):
                        raise ValidationError(_('The Distance Between zip codes (%s) and (%s) is too small that the distance required to (%s) miles'% (zip_code , single_code, max_distance_mel)))