# -*- coding: utf-8 -*-
import requests
import json
from odoo.tools import email_normalize
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError




class Survey(models.Model):
    _inherit = 'survey.survey'
    
    ptse_type = fields.Selection([
        ('ptse_1','PTSE 1'),
        ('ptse_2','PTSE 2')
    ], required=True)