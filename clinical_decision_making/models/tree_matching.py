# -*- coding: utf-8 -*-

import requests
from lxml.etree import LxmlError
from lxml import etree
import json
from datetime import date
import datetime
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class TreeMatching(models.Model):
    _name = 'tree.matching'
    _description = 'Tree matching Student'
    _rec_name = 'student_id'
    _order = 'request_id desc, id desc'

    active = fields.Boolean(default=True)
    request_id = fields.Many2one(comodel_name='placement.request', string='Request', ondelete='cascade')
    parent_state = fields.Selection(related='request_id.state')
        
    # Student Information
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', domain=[('is_student', '=', True)], readonly=True)
    first_name = fields.Char(related='student_id.first_name')
    last_name = fields.Char(related='student_id.last_name')
    cohort_label = fields.Char(related='student_id.cohort_label')
    stu_email = fields.Char(related='student_id.email')
    stu_phone = fields.Char(related='student_id.phone')
    home_address = fields.Char(related='student_id.home_address')
    

    tree_state = fields.Selection([
        ('approved_pp', 'Approved ++'),
        ('approved_p', 'Approved +'),
        ('not_confirm_state', 'not Confirm State'),
        ('not_accepet_dis', 'Not Accepet Dis'),
        ('draft', 'Draft'),

    ], string='tree_prograss',
        compute='_compute_tree_state_prograss',
        store=True,
    )
    
    
    @api.depends('parent_state')
    def _compute_tree_state_prograss(self):
        if self.request_id:
            for rec in self.request_id.tree_ids:
                    if rec.hardship_status == 'approved':
                        rec.tree_state = 'approved_pp'
                    elif rec.placement_status == 'done':
                        rec.tree_state = 'not_confirm_state'
                    else:
                        rec.tree_state = 'draft'

    #-----------------------------------
    # Student Locations
        # One
    stu_locatio_zip_one = fields.Char(string='Zip Code One', compute='compute_student_locations', store=True)
    stu_locatio_city_one_id = fields.Char(string='City One', compute='compute_student_locations', store=True)
    stu_locatio_state_one_id =fields.Char(string='State One', compute='compute_student_locations', store=True)
        
        # Two
    stu_locatio_zip_two = fields.Char(string='Zip Code Two', compute='compute_student_locations', store=True)
    stu_locatio_city_two_id = fields.Char(string='City Two', compute='compute_student_locations', store=True)
    stu_locatio_state_two_id =fields.Char(string='State Two', compute='compute_student_locations', store=True)
        
        # THREE
    stu_locatio_zip_three = fields.Char(string='Zip Code Three', compute='compute_student_locations', store=True)
    stu_locatio_city_three_id = fields.Char(string='City Three', compute='compute_student_locations', store=True)
    stu_locatio_state_three_id =fields.Char(string='State Three', compute='compute_student_locations', store=True)
        
        # FOUR
    stu_locatio_zip_four = fields.Char(string='Zip Code Four', compute='compute_student_locations', store=True)
    stu_locatio_city_four_id = fields.Char(string='City Four', compute='compute_student_locations', store=True)
    stu_locatio_state_four_id =fields.Char(string='State Four', compute='compute_student_locations', store=True)
        
        # FIVE
    stu_locatio_zip_five = fields.Char(string='Zip Code Five', compute='compute_student_locations', store=True)
    stu_locatio_city_five_id = fields.Char(string='City Five', compute='compute_student_locations', store=True)
    stu_locatio_state_five_id =fields.Char(string='State Five', compute='compute_student_locations', store=True)
    
    @api.depends('student_id')
    def compute_student_locations(self):
        for rec in self:
            
            lines = len(rec.student_id.geographical_ids)
            
            rec.stu_locatio_zip_one = rec.student_id.geographical_ids[0].zip_code if lines  >= 1 else False
            rec.stu_locatio_city_one_id = rec.student_id.geographical_ids[0].city if lines  >= 1 else False
            rec.stu_locatio_state_one_id = rec.student_id.geographical_ids[0].state if lines  >= 1 else False
            
            rec.stu_locatio_zip_two = rec.student_id.geographical_ids[1].zip_code if lines  >= 2 else False
            rec.stu_locatio_city_two_id = rec.student_id.geographical_ids[1].city if lines  >= 2 else False
            rec.stu_locatio_state_two_id = rec.student_id.geographical_ids[1].state if lines  >= 2 else False
            
            rec.stu_locatio_zip_three = rec.student_id.geographical_ids[2].zip_code if lines  >= 3 else False
            rec.stu_locatio_city_three_id = rec.student_id.geographical_ids[2].city if lines  >= 3 else False
            rec.stu_locatio_state_three_id = rec.student_id.geographical_ids[2].state if lines  >= 3 else False
            
            rec.stu_locatio_zip_four = rec.student_id.geographical_ids[3].zip_code if lines  >= 4 else False
            rec.stu_locatio_city_four_id = rec.student_id.geographical_ids[3].city if lines  >= 4 else False
            rec.stu_locatio_state_four_id = rec.student_id.geographical_ids[3].state if lines  >= 4 else False
            
            rec.stu_locatio_zip_five = rec.student_id.geographical_ids[4].zip_code if lines  >= 5 else False
            rec.stu_locatio_city_five_id = rec.student_id.geographical_ids[4].city if lines  >= 5 else False
            rec.stu_locatio_state_five_id = rec.student_id.geographical_ids[4].state if lines  >= 5 else False
              
    
    hardship_status = fields.Selection([
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved'),
    ], string='Hardship Status', compute='_compute_hardship_status', store=True, precompute=True)
    
    
    @api.depends('student_id', 'student_id.hardship_ids', 'student_id.hardship_ids.state')
    def _compute_hardship_status(self):
        for rec in self:
            if rec.parent_state == 'running':
                hardship_id = rec.student_id.hardship_ids
                if hardship_id:
                    rec.hardship_status = 'approved' if hardship_id.state == 'confirm' else 'not_approved'
                else:
                    rec.hardship_status = False
    
    # ------------------------------------------------------------------------------
    
    # Placement 
        # Site Setting
        
    aval_facility_id = fields.Many2many(comodel_name='medical.facility', string='Aval medical.facility' ,compute='_compute_aval_facility_id')
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Clinical Site')
    offer_id = fields.Many2one(comodel_name='placement.offer', realted='offer_line_id.offer_id')
    offer_line_id = fields.Many2one(comodel_name='placement.offer.line', string="Setting Intership")
    setting = fields.Selection(related='offer_line_id.setting')
    
    
    address = fields.Char(related='facility_id.address')
    email = fields.Char(related='facility_id.email')
    
    geographical_id = fields.Many2one(comodel_name='geographical', related='facility_id.geographical_id')
    city = fields.Char(related='facility_id.city')
    state = fields.Char(related='facility_id.state')

        # SCCE
    aval_scce_ids = fields.Many2many(comodel_name='scce', compute='_compute_aval_scce_ids')
    scce_id = fields.Many2one('scce', string='SCCE')
    scce_first_name = fields.Char(related='scce_id.first_name')
    scce_last_name = fields.Char(related='scce_id.last_name')
    scce_email = fields.Char(related='scce_id.email')

        # Accepter
    placement_status = fields.Selection([('normal', 'Pending'), ('done', 'Confirmed'), ('blocked', 'Not Placed')], default='blocked', string='Placement Status')

    @api.onchange('facility_id')
    def setting_id_domain(self):
        self.scce_id = False
        return {
            'domain':
                {
                    'scce_id': [('id', 'in', self.facility_id.scce_primary_id.id)],
                },
        }

    
    @api.depends('facility_id', 'scce_id')
    def _compute_aval_scce_ids(self):
        for rec in self:
            if rec.facility_id:
                rec.aval_scce_ids = rec.facility_id.scce_primary_id
            else:
                rec.aval_scce_ids = False 
                
    @api.depends('student_id')
    def _compute_aval_facility_id(self):
        for rec in self:
            # facility_ids = self.search([('student_id', '=', rec.student_id.id), ('parent_state', '=', 'done')])
            # ice_facility_ids = facility_ids.mapped('ice_facility_id').ids
            # # facility_ids = facility_ids.mapped('facility_id').ids
            # tce2_facility_ids = facility_ids.mapped('tce2_facility_id').ids
            # ids = list(set(ice_facility_ids + tce2_facility_ids))
            rec.aval_facility_id = False #self.env['site'].search([('id', 'in', rec.request_id.info_ids.mapped('clinc_id').ids), ('id', 'not in', ids)])
            
                
    # ------------------------------------------------------------------------------

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, options=options)
        if view_type == 'tree':
            doc = etree.fromstring(res['arch'])
            list_field = ['description', 'timesheet_ids']
            for field in self._fields:
                if field not in list_field:
                    field_xpath = "//field[@name='%s']" % field
                    nodes = doc.xpath(field_xpath)
                    for node in nodes:
                        modifiers = json.loads(node.get('modifiers') or '{}')
                        modifiers['readonly'] = [['parent_state', '=', 'doen']]
                        node.set('modifiers', json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res