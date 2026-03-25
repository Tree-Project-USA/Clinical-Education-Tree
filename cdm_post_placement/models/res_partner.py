# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    plcement_management_ids = fields.One2many(comodel_name='post.plcement.management', inverse_name='student_id', string='Post Placement Management')
