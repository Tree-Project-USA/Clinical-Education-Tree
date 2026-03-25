# -*- coding: utf-8 -*-
from odoo import models, fields

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    ptse_type = fields.Selection([
        ('ptse_1', 'PTSE 1'),
        ('ptse_2', 'PTSE 2'),
    ], string='PTSE Type')
