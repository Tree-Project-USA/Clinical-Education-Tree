# -*- coding: utf-8 -*-
import requests
import json
from odoo import models, fields, api, _

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
        
    @api.onchange('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.first_name if rec.first_name else '' + ', ' + rec.last_name if rec.last_name else ''
    