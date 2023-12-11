# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Program(models.Model):
    _name = 'program'
    _description = 'Student Program'
    _rec_name = 'name'
    
    name = fields.Char(string='Name')
    num_terms = fields.Integer(string='Number of terms', default=1)
    active = fields.Boolean(string='Active')
    ice_term = fields.Integer(string='ICE term Number')
    tce1_term = fields.Integer(string='TCE1 term Number')
    tce2_term = fields.Integer(string='TCE2 term Number')
    
    
    
    