# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
    
    @api.constrains('num_terms', 'ice_term', 'tce1_term', 'tce2_term')
    def _check_num_terms(self):
        for rec in self:
            if rec.ice_term > rec.num_terms or rec.tce1_term > rec.num_terms or rec.tce2_term > rec.num_terms:
                raise ValidationError("Number of terms must be greater than any other field.")