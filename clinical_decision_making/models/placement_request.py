# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PlacementRequest(models.Model):
    _name = 'placement.request'
    _inherit = ['mail.thread']
    _description = 'Placement Request'
    _rec_name = 'name'
    
    name = fields.Char(string='Test')
    
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students')
    line_ids = fields.Many2many(comodel_name='placement.offer.line', string='')
    new_field = fields.Many2many(comodel_name='', string='')
    
    
    # Filters
    student_id = fields.Many2one(comodel_name='res.partner', string='Student',domain=[('is_student', '=', True)])
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce1', 'TCE1'),
        ('tce2', 'TCE2'),
    ], string='Type')
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term')
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Facility')
    
    
    
    