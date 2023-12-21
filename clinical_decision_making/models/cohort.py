# -*- coding: utf-8 -*-

import requests
from lxml.etree import LxmlError
from datetime import date
import datetime
from odoo import models, fields, api,_
from odoo.addons.clinical_decision_making.models.setting import get_distance
from odoo.exceptions import ValidationError

class Cohort(models.Model):
    _name = 'cohort'
    _description = 'Cohort'
    _rec_name = 'cpdm_tree_id'

    active = fields.Boolean(default=True)
    cpdm_tree_id = fields.Many2one(comodel_name='cpdm.tree', string='cpdm Tree', ondelete='cascade')
    parent_state = fields.Selection(related='cpdm_tree_id.state')
    parent_type = fields.Selection(related='cpdm_tree_id.type')
        
    # Student Information
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', domain=[('is_student', '=', True)], readonly=True)
    first_name = fields.Char(related='student_id.first_name')
    last_name = fields.Char(related='student_id.last_name')
    cohort_label = fields.Char(related='student_id.cohort_label')
    stu_email = fields.Char(related='student_id.email')
    stu_phone = fields.Char(related='student_id.phone')
    home_address = fields.Char(related='student_id.home_address')
    
    def get_default_avalible_student_ids(self):
        cpdm_tree_id = self.env['cpdm.tree'].browse(self.env.context.get('default_cpdm_tree_id'))
        avalible_student_ids = self.env['res.partner'].sudo().search([('is_student', '=', True), ('cohort_label', '=', cpdm_tree_id.cohort_labels), ('id', 'not in', cpdm_tree_id.cohort_ids.mapped('student_id').ids)])
        return avalible_student_ids
    
    avalible_student_ids = fields.Many2many(comodel_name='res.partner', string='Avalible Student', domain=[('is_student', '=', True)], default=get_default_avalible_student_ids, readonly=True)    
    stu_setting_one_id = fields.Many2one(comodel_name='category.setting', string="Setting One")
    stu_setting_two_id = fields.Many2one(comodel_name='category.setting', string="Setting Two")
    stu_setting_three_id = fields.Many2one(comodel_name='category.setting', string="Setting Three")
    
    tree_state = fields.Selection([
        ('approved_pp', 'Approved ++'),
        ('approved_p', 'Approved +'),
        ('not_confirm_state', 'not Confirm State'),
        ('not_accepet_dis', 'Not Accepet Dis'),
        ('draft', 'Draft'),

    ], string='tree_prograss',
        compute='_compute_tree_state_prograss',
    )
    @api.depends('parent_state')
    def _compute_tree_state_prograss(self):
        for rec in self.cpdm_tree_id.cohort_ids:
                if rec.hardship_status == 'approved' and rec.cat_one_requirment == 'met':
                    rec.tree_state = 'approved_pp'
                elif rec.cat_one_requirment == 'met':
                    rec.tree_state = 'approved_p'
                elif rec.ice_placement_status == 'done':
                    rec.tree_state = 'not_confirm_state'
                elif rec.ice_accepted_distances == 'accepted':
                    rec.tree_state = 'not_accepet_dis'
                else:
                    rec.tree_state = 'draft'
    
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
    
        
    @api.depends('student_id.locatio_ids')
    def _compute_intershi_ice(self):
        for rec in self:
            archive_id = rec.student_id.archive_ids.filtered(lambda setting_id : setting_id.intership_period == 'ice')
            rec.stu_setting_one_id = archive_id.setting_id
            
    @api.depends('student_id.locatio_ids')
    def _compute_intershi_tce1(self):
        for rec in self:
            archive_id = rec.student_id.archive_ids.filtered(lambda setting_id : setting_id.intership_period == 'tce1')
            rec.stu_setting_two_id = archive_id.setting_id
            
    @api.depends('student_id.locatio_ids')
    def _compute_intershi_tce2(self):
        for rec in self:
            archive_id = rec.student_id.archive_ids.filtered(lambda setting_id : setting_id.intership_period == 'tce2')
            rec.stu_setting_three_id = archive_id.setting_id
            
    @api.depends('student_id', 'student_id.locatio_ids')
    def compute_student_locations(self):
        for rec in self:
            
            lines = len(rec.student_id.locatio_ids)
            
            rec.stu_locatio_zip_one = rec.student_id.locatio_ids[0].zip if lines  >= 1 else False
            rec.stu_locatio_city_one_id = rec.student_id.locatio_ids[0].city if lines  >= 1 else False
            rec.stu_locatio_state_one_id = rec.student_id.locatio_ids[0].state if lines  >= 1 else False
            
            rec.stu_locatio_zip_two = rec.student_id.locatio_ids[1].zip if lines  >= 2 else False
            rec.stu_locatio_city_two_id = rec.student_id.locatio_ids[1].city if lines  >= 2 else False
            rec.stu_locatio_state_two_id = rec.student_id.locatio_ids[1].state if lines  >= 2 else False
            
            rec.stu_locatio_zip_three = rec.student_id.locatio_ids[2].zip if lines  >= 3 else False
            rec.stu_locatio_city_three_id = rec.student_id.locatio_ids[2].city if lines  >= 3 else False
            rec.stu_locatio_state_three_id = rec.student_id.locatio_ids[2].state if lines  >= 3 else False
            
            rec.stu_locatio_zip_four = rec.student_id.locatio_ids[3].zip if lines  >= 4 else False
            rec.stu_locatio_city_four_id = rec.student_id.locatio_ids[3].city if lines  >= 4 else False
            rec.stu_locatio_state_four_id = rec.student_id.locatio_ids[3].state if lines  >= 4 else False
            
            rec.stu_locatio_zip_five = rec.student_id.locatio_ids[4].zip if lines  >= 5 else False
            rec.stu_locatio_city_five_id = rec.student_id.locatio_ids[4].city if lines  >= 5 else False
            rec.stu_locatio_state_five_id = rec.student_id.locatio_ids[4].state if lines  >= 5 else False
                   
    #-----------------------------------
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
    
    # Met Rquirements
    cat_one_requirment = fields.Selection([('not_met', 'Not Met'), ('met', 'Met'),], string='CAT 1 Requirment', compute='_compute_cat_one_requirment', store=True)
    met_via = fields.Selection([('not_met', 'Not Met'), ('met_via_ice', 'Met via ICE'), ('met_via_tce_1', 'Met via TCE I'), ('met_via_tce_2', 'Met via TCE II')], string='Via CE', compute='_compute_cat_one_requirment', store=True)
    pta_supervision = fields.Selection([('normal', ''), ('done', 'Met'), ('blocked', 'Not Met')], default='normal', string='PTA Supervision')
    ipe = fields.Selection([('normal', ''), ('done', 'Met'), ('blocked', 'Not Met')], default='normal', string='IPE')
   
        
    @api.depends('stu_setting_one_id', 'stu_setting_two_id', 'stu_setting_three_id', 'ice_setting_id', 'tce1_setting_id', 'tce2_setting_id', 'pta_supervision', 'ipe', 'ice_placement_status', 'tce1_placement_status', 'tce2_placement_status', 'ice_accepted_distances', 'tce1_accepted_distances', 'tce2_accepted_distances')
    def _compute_cat_one_requirment(self):
        for rec in self:
            if rec.parent_state == 'running':
                if rec.parent_type == 'ice' and rec.pta_supervision == 'done' and rec.ipe == 'done' and rec.ice_placement_status == 'done' and rec.ice_accepted_distances == 'accepted':
                    rec.cat_one_requirment = 'met'
                elif rec.parent_type == 'tce1' and rec.pta_supervision == 'done' and rec.ipe == 'done' and rec.tce1_placement_status == 'done' and rec.tce1_accepted_distances == 'accepted':
                    rec.cat_one_requirment = 'met'
                elif rec.parent_type == 'tce2' and rec.pta_supervision == 'done' and rec.ipe == 'done' and rec.tce2_placement_status == 'done' and rec.tce2_accepted_distances == 'accepted':
                    rec.cat_one_requirment = 'met'
                else:
                    rec.cat_one_requirment = 'not_met'

                if rec.ice_setting_id and rec.ice_setting_id in [rec.stu_setting_one_id, rec.stu_setting_two_id, rec.stu_setting_three_id]:
                    rec.met_via = 'met_via_ice'
                elif rec.tce1_setting_id and rec.tce1_setting_id in [rec.stu_setting_one_id, rec.stu_setting_two_id, rec.stu_setting_three_id]:
                    rec.met_via = 'met_via_tce_1'
                elif rec.tce2_setting_id and rec.tce2_setting_id in [rec.stu_setting_one_id, rec.stu_setting_two_id, rec.stu_setting_three_id]:
                    rec.met_via = 'met_via_tce_2'
                else:
                    rec.met_via = 'not_met'                

    # Placement ICE
        # Site Setting
    aval_ice_setting_ids = fields.Many2many(comodel_name='category.setting', compute='_compute_aval_ice_setting_ids')
    ice_setting_id =  fields.Many2one(comodel_name='category.setting', string="Setting")
    ice_setting_code = fields.Selection(related='ice_setting_id.code')
    aval_ice_site_id = fields.Many2many(comodel_name='site', compute='_compute_aval_ice_site_id')
    ice_site_id = fields.Many2one(comodel_name='site', string='ICE Site Name')
    ice_site_address = fields.Char(related='ice_site_id.address')
    ice_city = fields.Char(related='ice_site_id.city')
    ice_state = fields.Char(related='ice_site_id.state')
    ice_zip = fields.Char(related='ice_site_id.zip')
    
        # SCCE
    aval_ice_scce_ids = fields.Many2many(comodel_name='scce', compute='_compute_aval_ice_scce_ids', store=True)
    ice_scce_id = fields.Many2one('scce', string='ICE SCCE')
    
    ice_scce_first_name = fields.Char(related='ice_scce_id.first_name')
    ice_scce_last_name = fields.Char(related='ice_scce_id.last_name')
    ice_scce_email = fields.Char(related='ice_scce_id.email')

        # Accepter
    ice_placement_status = fields.Selection([('normal', 'Pending'), ('done', 'Confirmed'), ('blocked', 'Not Placed')], default='blocked', string='ICE Placement Status')
    ice_accepted_distances = fields.Selection([
        ('accepted', 'Accepted Dist'),
        ('not_accepted', 'Not Accepted Dist'),
    ], string='ICE Accepted Distances', compute='_compute_accepted_distances', store=True)
    
    @api.onchange('ice_site_id')
    def ice_setting_id_domain(self):
        self.ice_setting_id = False
        self.ice_scce_id = False
        return {
            'domain':
                {
                    'ice_setting_id': [('id', 'in', self.ice_site_id.setting_ids.ids)],
                    'ice_scce_id': [('id', 'in', self.ice_site_id.scce_ids.ids)],
                },
        }

    @api.depends('ice_site_id', 'ice_setting_id')
    def _compute_aval_ice_setting_ids(self):
        for rec in self:
            if rec.ice_site_id:
                f_code = rec.cpdm_tree_id.info_ids.filtered(lambda x : x.clinc_id == rec.ice_site_id).mapped('setting_type')
                print(f_code)
                print(rec.ice_site_id)
                print(rec.ice_site_id.setting_ids)
                print(rec.ice_site_id.setting_ids.filtered(lambda x : x.code in f_code))
                rec.aval_ice_setting_ids = rec.ice_site_id.setting_ids.filtered(lambda x : x.code in f_code)
            else:
                rec.aval_ice_setting_ids = False 
                
    @api.depends('ice_site_id', 'ice_scce_id')
    def _compute_aval_ice_scce_ids(self):
        for rec in self:
            if rec.ice_site_id:
                rec.aval_ice_scce_ids = rec.ice_site_id.scce_ids
            else:
                rec.aval_ice_scce_ids = False 
        
    @api.depends('student_id')
    def _compute_aval_ice_site_id(self):
        for rec in self:
            site_ids = self.search([('student_id', '=', rec.student_id.id), ('parent_state', '=', 'done')])
            # ice_site_ids = site_ids.mapped('ice_site_id').ids
            tce1_site_ids = site_ids.mapped('tce1_site_id').ids
            tce2_site_ids = site_ids.mapped('tce2_site_id').ids
            ids = list(set(tce1_site_ids + tce2_site_ids))
            
            rec.aval_ice_site_id = self.env['site'].search([('id', 'in', rec.cpdm_tree_id.info_ids.mapped('clinc_id').ids), ('id', 'not in', ids)])
            
    # ------------------------------------------------------------------------------
    
    # Placement TCE 1
        # Site Setting
    aval_tce1_setting_id = fields.Many2many(comodel_name='category.setting', compute='_compute_aval_tce1_setting_id')
    tce1_setting_id =  fields.Many2one(comodel_name='category.setting', string="TCE I Setting")
    tce1_setting_code = fields.Selection(related='tce1_setting_id.code')
    aval_tce1_site_id = fields.Many2many(comodel_name='site', string='Aval tce1' ,compute='_compute_aval_tce1_site_id')
    tce1_site_id = fields.Many2one(comodel_name='site', string='TCE I Site Name')
    tce1_site_address = fields.Char(related='ice_site_id.address')
    tce1_city = fields.Char(related='ice_site_id.city')
    tce1_state = fields.Char(related='ice_site_id.state')
    tce1_zip = fields.Char(related='ice_site_id.zip')
    
        # SCCE
    aval_tce1_scce_ids = fields.Many2many(comodel_name='scce', compute='_compute_aval_tce1_scce_ids')
    tce1_scce_id = fields.Many2one('scce', string='TCE I SCCE')
    tce1_scce_first_name = fields.Char(related='ice_scce_id.first_name')
    tce1_scce_last_name = fields.Char(related='ice_scce_id.last_name')
    tce1_scce_email = fields.Char(related='ice_scce_id.email')

        # Accepter
    tce1_placement_status = fields.Selection([('normal', 'Pending'), ('done', 'Confirmed'), ('blocked', 'Not Placed')], default='blocked', string='TCE I Placement Status')
    tce1_accepted_distances = fields.Selection([
        ('accepted', 'Accepted Dist'),
        ('not_accepted', 'Not Accepted Dist'),
    ], string='TCE II Accepted Distances', compute='_compute_accepted_distances', store=True)
    
    @api.onchange('tce1_site_id')
    def tce1_setting_id_domain(self):
        self.tce1_setting_id = False
        self.tce1_scce_id = False
        return {
            'domain':
                {
                    'tce1_setting_id': [('id', 'in', self.tce1_site_id.setting_ids.ids)],
                    'tce1_scce_id': [('id', 'in', self.tce1_site_id.scce_ids.ids)],
                },
        }

    @api.depends('tce1_site_id', 'tce1_setting_id')
    def _compute_aval_tce1_setting_id(self):
        for rec in self:
            if rec.tce1_site_id:
                ip_setting = self.search([('student_id', '=', rec.student_id.id), ('parent_state', '=', 'done'), '|', ('ice_setting_code', '=', 'ip'), ('tce2_setting_code', '=', 'ip'), ])
                if ip_setting:
                    rec.aval_tce1_setting_id = rec.tce1_site_id.setting_ids.filtered(lambda x: x.code == 'op')
                else:
                    rec.aval_tce1_setting_id = rec.tce1_site_id.setting_ids
                    
            else:
                rec.aval_tce1_setting_id = False 
                
    @api.depends('tce1_site_id', 'tce1_scce_id')
    def _compute_aval_tce1_scce_ids(self):
        for rec in self:
            if rec.tce1_site_id:
                rec.aval_tce1_scce_ids = rec.tce1_site_id.scce_ids
            else:
                rec.aval_tce1_scce_ids = False 
                
    @api.depends('student_id')
    def _compute_aval_tce1_site_id(self):
        for rec in self:
            site_ids = self.search([('student_id', '=', rec.student_id.id), ('parent_state', '=', 'done')])
            ice_site_ids = site_ids.mapped('ice_site_id').ids
            # tce1_site_ids = site_ids.mapped('tce1_site_id').ids
            tce2_site_ids = site_ids.mapped('tce2_site_id').ids
            ids = list(set(ice_site_ids + tce2_site_ids))
            rec.aval_tce1_site_id = self.env['site'].search([('id', 'in', rec.cpdm_tree_id.info_ids.mapped('clinc_id').ids), ('id', 'not in', ids)])
            
                
    # ------------------------------------------------------------------------------
    
    # Placement TCE 2
        # Site Setting
    aval_tce2_setting_id = fields.Many2many(comodel_name='category.setting', compute='_compute_aval_tce2_setting_id')
    tce2_setting_id =  fields.Many2one(comodel_name='category.setting', string="TCE II Setting")
    tce2_setting_code = fields.Selection(related='tce2_setting_id.code')
    aval_tce2_site_id = fields.Many2many(comodel_name='site', compute='_compute_aval_tce2_site_id')
    tce2_site_id = fields.Many2one(comodel_name='site', string='TCE II Site Name')
    tce2_site_address = fields.Char(related='ice_site_id.address')
    tce2_city = fields.Char(related='ice_site_id.city')
    tce2_state = fields.Char(related='ice_site_id.state')
    tce2_zip = fields.Char(related='ice_site_id.zip')
    
        # SCCE
    aval_tce2_scce_ids = fields.Many2many(comodel_name='scce', compute='_compute_aval_tce2_scce_ids')
    tce2_scce_id = fields.Many2one('scce', string='TCE II SCCE')
    tce2_scce_first_name = fields.Char(related='ice_scce_id.first_name')
    tce2_scce_last_name = fields.Char(related='ice_scce_id.last_name')
    tce2_scce_email = fields.Char(related='ice_scce_id.email')

        # Accepter
    tce2_placement_status = fields.Selection([('normal', 'Pending'), ('done', 'Confirmed'), ('blocked', 'Not Placed')], default='blocked', string='TCE II Placement Status')
    tce2_accepted_distances = fields.Selection([
        ('accepted', 'Accepted Dist'),
        ('not_accepted', 'Not Accepted Dist'),
    ], string='TCE II Accepted Distances', compute='_compute_accepted_distances', store=True)
    
    @api.onchange('tce2_site_id')
    def tce2_setting_id_domain(self):
        self.tce2_setting_id = False
        self.tce2_scce_id = False
        return {
            'domain':
                {
                    'tce2_setting_id': [('id', 'in', self.tce2_site_id.setting_ids.ids)],
                    'tce2_scce_id': [('id', 'in', self.tce2_site_id.scce_ids.ids)],
                },
        }

    @api.depends('tce2_site_id', 'tce1_setting_id')
    def _compute_aval_tce2_setting_id(self):
        for rec in self:
            if rec.tce2_site_id:
                ip_setting = self.search([('student_id', '=', rec.student_id.id), ('parent_state', '=', 'done'), '|', ('ice_setting_code', '=', 'ip'), ('tce1_setting_code', '=', 'ip')])
                if ip_setting:
                    rec.aval_tce2_setting_id = rec.tce2_site_id.setting_ids.filtered(lambda x: x.code == 'op')
                else:
                    rec.aval_tce2_setting_id = rec.tce2_site_id.setting_ids
            else:
                rec.aval_tce2_setting_id = False 
                
    @api.depends('tce2_site_id', 'tce2_scce_id')
    def _compute_aval_tce2_scce_ids(self):
        for rec in self:
            if rec.tce2_site_id:
                rec.aval_tce2_scce_ids = rec.tce2_site_id.scce_ids
            else:
                rec.aval_tce2_scce_ids = False 
                
    @api.depends('student_id')
    def _compute_aval_tce2_site_id(self):
        for rec in self:
            site_ids = self.search([('student_id', '=', rec.student_id.id), ('parent_state', '=', 'done')])
            ice_site_ids = site_ids.mapped('ice_site_id').ids
            tce1_site_ids = site_ids.mapped('tce1_site_id').ids
            # tce2_site_ids = site_ids.mapped('tce2_site_id').ids
            ids = list(set(ice_site_ids + tce1_site_ids))
            rec.aval_tce2_site_id = self.env['site'].search([('id', 'in', rec.cpdm_tree_id.info_ids.mapped('clinc_id').ids), ('id', 'not in', ids)])
            
    # ------------------------------------------------------------------------------

    @api.depends(
        'stu_locatio_zip_one',
        'stu_locatio_zip_two',
        'stu_locatio_zip_three',
        'stu_locatio_zip_four',
        'stu_locatio_zip_five',
        'ice_site_id', 
        'tce1_site_id', 
        'tce2_site_id')
    def _compute_accepted_distances(self):
        clinical_distance_mel = self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')
        def check_accepted_distance(zip_code_one, zip_code_two):
            if zip_code_one and zip_code_two:
                distance = get_distance(zip_code_one, zip_code_two)
                return float(distance) <= float(clinical_distance_mel)
            return False
        for rec in self:
            rec.ice_accepted_distances = 'not_accepted'
            rec.tce1_accepted_distances = 'not_accepted'
            rec.tce2_accepted_distances = 'not_accepted'

            ice_zip_code = rec.ice_site_id.zip if rec.ice_site_id else False
            tce1_zip_code = rec.tce1_site_id.zip if rec.tce1_site_id else False
            tce2_zip_code = rec.tce2_site_id.zip if rec.tce2_site_id else False
            stu_codes = [rec.stu_locatio_zip_one,
                        rec.stu_locatio_zip_two,
                        rec.stu_locatio_zip_three,
                        rec.stu_locatio_zip_four,
                        rec.stu_locatio_zip_five]
            
            for code in stu_codes:
                if code and code != '0' and ice_zip_code and check_accepted_distance(code, ice_zip_code):
                    rec.ice_accepted_distances = 'accepted'
                    break
                
            for code in stu_codes:
                if code and code != '0' and tce1_zip_code and check_accepted_distance(code, tce1_zip_code):
                    rec.tce1_accepted_distances = 'accepted'
                    break
            for code in stu_codes:
                if code and code != '0' and tce2_zip_code and check_accepted_distance(code, tce2_zip_code):
                    rec.tce2_accepted_distances = 'accepted'
                    break
        
    
    def action_send_email_to_students(self):
        for rec in self:
            if rec.student_id.email:
                mail = (
                            self.env["mail.mail"]
                            .sudo()
                            .create(
                                {
                                    "subject": _("Test Student Upadte Information"),
                                    "email_from": self.env.company.email,
                                    "body_html": "Dear :- {},<br/>Update Your Information <br/><br/>Thank you,<br/>".format(
                                        rec.student_id.name
                                    ),
                                    "email_to": rec.student_id.email,
                                }
                            )
                            )
                mail.send()
    
class CPDMTree(models.Model):
    _name = 'cpdm.tree'
    _description = 'Cohort'
    _rec_name = 'name'
    _order = 'priority desc, id desc'
    
    def get_cohort_label(self):
        cohort_labels = self.env['res.partner'].sudo().search([('is_student', '=', True)]).mapped('cohort_label')
        selection = [(item, item) for item in list(set(cohort_labels))]
        return selection

    name = fields.Char(string='Name', required=True)
    sequence_number = fields.Char(string='Sequence', required=True, index=True, copy=False, default='New')
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True)
    # placement_ids = fields.Many2one(comodel_name='placement.setting', string='Placement')
    cpdm_date = fields.Date('cpdm Date',default=fields.Date.today())
    
    date_begin = fields.Datetime('Start Date')
    date_end = fields.Datetime('End Date')
        
    cohort_ids = fields.One2many(comodel_name='cohort', inverse_name='cpdm_tree_id', string='Cpdm Tree', ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
    ], string='state',default='draft')
    total_students  = fields.Integer(compute='_compute_total_students', string='Total Students')
    total_confirmed  = fields.Integer(compute='_compute_total_students', string='Confirmed')
    total_pending  = fields.Integer(compute='_compute_total_students', string='Pending')
    total_not_placed  = fields.Integer(compute='_compute_total_students', string='Not Placed')
    total_hardships   = fields.Integer(compute='_compute_total_students', string='Total Hardships')
    comment = fields.Html(string='Notes')
    info_ids = fields.One2many('clinic.info.gathering', 'tree_id', string='Clinic Information Gathering')
    cohort_labels = fields.Selection(selection=get_cohort_label, string='Cohort Labels', required=True)
    is_bot = fields.Boolean(string='')
    type = fields.Selection([
        ('ice', 'ICE'),
        ('tce1', 'TCE1'),
        ('tce2', 'TCE2'),
    ], string='Type', required=True)
    term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term', required=True)
    date = fields.Date(string='Year', required=True)


    def open_hardship_button(self):
        context = {'default_cpdm_tree_id': self.id, 'create': False, 'delete': False}
        if self.state == 'done':
            context.update({'edite': False})
        if self.type == 'ice':
            tree_view_id = self.env.ref('clinical_decision_making.cohort_view_tree_ice').id
            
        elif self.type == 'tce1':
            tree_view_id = self.env.ref('clinical_decision_making.cohort_view_tree_tce1').id
        elif self.type == 'tce2':
            tree_view_id = self.env.ref('clinical_decision_making.cohort_view_tree_tce2').id
        else:
            tree_view_id = self.env.ref('clinical_decision_making.cohort_view_tree').id
        return {
            "type": "ir.actions.act_window",
            "name": _("Placement"),
            "res_model": "cohort",
            "domain": [['cpdm_tree_id', '=', self.id]],
            "views": [[tree_view_id, "tree"], [False, "form"]],
            "context": context
        }

    def open_hardship_button_not_Placed(self):
        tree_view_id = self.env.ref('clinical_decision_making.cohort_view_tree').id
        return {
            "type": "ir.actions.act_window",
            "name": _("Placement"),
            "res_model": "cohort",
            "domain": [('cpdm_tree_id', '=', self.id),('cpdm_tree_id.ice_placement_status','=','blocked')],
            "views": [[tree_view_id, "tree"], [False, "form"]],
            "context": {'default_cpdm_tree_id': self.id}
        }
    def open_hardship_button_confirmed(self):
        tree_view_id = self.env.ref('clinical_decision_making.cohort_view_tree').id
        return {
            "type": "ir.actions.act_window",
            "name": _("Placement"),
            "res_model": "cohort",
            "domain": [('cpdm_tree_id', '=', self.id),('cpdm_tree_id.ice_placement_status','=','done')],
            "views": [[tree_view_id, "tree"], [False, "form"]],
            "context": {'default_cpdm_tree_id': self.id}
        }
    def open_hardship_button_Pinding(self):
        tree_view_id = self.env.ref('clinical_decision_making.cohort_view_tree').id
        return {
            "type": "ir.actions.act_window",
            "name": _("Placement"),
            "res_model": "cohort",
            "domain": [('cpdm_tree_id', '=', self.id),('cpdm_tree_id.ice_placement_status','=','normal')],
            "views": [[tree_view_id, "tree"], [False, "form"]],
            "context": {'default_cpdm_tree_id': self.id}
        }
        
    @api.depends('cohort_ids', 'type')
    def _compute_total_students(self):
        for rec in self:
            rec.total_students = len(rec.cohort_ids.mapped('student_id'))
            rec.total_hardships = len(rec.cohort_ids.filtered(lambda record: record.hardship_status == 'approved'))
            
            placement_status_field = ""
            if rec.type == 'ice':
                placement_status_field = 'ice_placement_status'
            elif rec.type == 'tce1' or rec.type == 'tci1':
                placement_status_field = 'tce1_placement_status'
            elif rec.type == 'tce2' or rec.type == 'tci2':
                placement_status_field = 'tce2_placement_status'
            rec.total_confirmed = len(rec.cohort_ids.filtered(lambda record: getattr(record, placement_status_field) == 'done'))
            rec.total_pending = len(rec.cohort_ids.filtered(lambda record: getattr(record, placement_status_field) == 'normal'))
            rec.total_not_placed = len(rec.cohort_ids.filtered(lambda record: getattr(record, placement_status_field) == 'blocked'))
            
    def action_post(self):
        self.ensure_one()
        
        if not self.info_ids:
            raise ValidationError("You should add Facility Info")
        
        if any(record.num_students == 0 for record in self.info_ids):
            raise ValidationError("Student number of all Facility should be greater than zero")
        
        domain = [('is_student', '=', True), ('cohort_label', '=', self.cohort_labels)]
        
        if self.type == 'ice':
            domain += [('is_complete_ice', '=', False)]
        elif self.type == 'tce1':
            domain += [('is_complete_tce1', '=', False)]
        elif self.type == 'tce2':
            domain += [('is_complete_tce2', '=', False)]
        student_ids = self.env['res.partner'].sudo().search(domain)
        student_in_progress = self.search([('id', '!=', self.id), ('type', '=', self.type), ('state', '=', 'running')]).mapped('cohort_ids').mapped('student_id')
        
        student_ids -= student_in_progress
        
        cohort_vals = []
        for student_id in student_ids:
            cohort_vals.append({
                'student_id': student_id.id,
                'cpdm_tree_id': self.id
            })
        
        if len(cohort_vals) == 0:
            raise ValidationError("Ther is no student to be matched")
        
        cohort_ids = self.env['cohort'].sudo().create(cohort_vals)
        self.write({
            'state': 'running',
        })
        if self.is_bot:
            self.run_automatching_process()
        # for rec in data:...
        # data = self.env['cohort'].sudo().create(cohort_vals)
        # for rec in data:...
            
    def run_automatching_process(self):
        clinical_distance_mel = self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')
        
        def check_accepted_distance(zip_code_one, zip_code_two):
            if zip_code_one and zip_code_two:
                distance = get_distance(zip_code_one, zip_code_two)
                return float(distance) <= float(clinical_distance_mel)
            return False

        def get_setting_id(site, code):
            if code == 'ip':
                return site.setting_ids.filtered(lambda x: x.code == 'ip')
            elif code == 'op':
                return site.setting_ids.filtered(lambda x: x.code == 'op')
            return False

        def get_scce_id(site):
            return site.scce_ids[0] if site.scce_ids else False

        for cohort_id in self.cohort_ids:
            site_ids = self.info_ids.mapped('clinc_id')

            if self.type == 'ice':
                for s_zip in cohort_id.student_id.locatio_ids.mapped('zip'):
                    for site_id in site_ids:
                        if check_accepted_distance(s_zip, site_id.zip):
                            cohort_id.ice_site_id = site_id
                            ip_setting = self.env['cohort'].search([('student_id', '=', cohort_id.student_id.id), ('parent_state', '=', 'done'), '|', ('tce1_setting_code', '=', 'ip'), ('tce2_setting_code', '=', 'ip'), ])
                            if ip_setting:
                                cohort_id.ice_setting_id = get_setting_id(cohort_id.ice_site_id, 'op') or False
                            else:
                                cohort_id.ice_setting_id = get_setting_id(cohort_id.ice_site_id, 'ip') or get_setting_id(cohort_id.ice_site_id, 'op') or False
                            cohort_id.ice_scce_id = get_scce_id(cohort_id.ice_site_id)
                            break

            elif self.type == 'tce1':
                for s_zip in cohort_id.student_id.locatio_ids.mapped('zip'):
                    for site_id in site_ids:
                        if check_accepted_distance(s_zip, site_id.zip):
                            cohort_id.tce1_site_id = site_id
                            ip_setting = self.env['cohort'].search([('student_id', '=', cohort_id.student_id.id), ('parent_state', '=', 'done'), '|', ('ice_setting_code', '=', 'ip'), ('tce2_setting_code', '=', 'ip'), ])
                            if ip_setting:
                                cohort_id.tce1_setting_id = get_setting_id(cohort_id.tce1_site_id, 'op') or False
                            else:
                                cohort_id.tce1_setting_id = get_setting_id(cohort_id.tce1_site_id, 'ip') or get_setting_id(cohort_id.tce1_site_id, 'op') or False
                            cohort_id.tce1_scce_id = get_scce_id(cohort_id.tce1_site_id)
                            break

            elif self.type == 'tce2':
                for s_zip in cohort_id.student_id.locatio_ids.mapped('zip'):
                    for site_id in site_ids:
                        if check_accepted_distance(s_zip, site_id.zip):
                            cohort_id.tce2_site_id = site_id
                            ip_setting = self.env['cohort'].search([('student_id', '=', cohort_id.student_id.id), ('parent_state', '=', 'done'), '|', ('ice_setting_code', '=', 'ip'), ('tce1_setting_code', '=', 'ip'), ])
                            if ip_setting:
                                cohort_id.tce2_setting_id = get_setting_id(cohort_id.tce2_site_id, 'op') or False
                            else:
                                cohort_id.tce2_setting_id = get_setting_id(cohort_id.tce2_site_id, 'ip') or get_setting_id(cohort_id.tce2_site_id, 'op') or False
                            cohort_id.tce2_scce_id = get_scce_id(cohort_id.tce2_site_id)
                            break
    
    def action_draft(self):
        self.write({
            'state': 'draft',
        })
    
    def get_data_from_type(self, record, ttype, dtype):
        field = ""
        if dtype == 'setting_id':
            if ttype == 'ice':
                field = 'ice_setting_id'
            elif ttype == 'tce1' or ttype == 'tci1':
                field = 'tce1_setting_id'
            elif ttype == 'tce2' or ttype == 'tci2':
                field = 'tce1_setting_id'
            
        if dtype == 'site_id':
            if ttype == 'ice':
                field = 'ice_site_id'
            elif ttype == 'tce1' or ttype == 'tci1':
                field = 'tce1_site_id'
            elif ttype == 'tce2' or ttype == 'tci2':
                field = 'tce2_site_id'
        if field != '':
            return getattr(record, field)
        else:
            return False
        
    def action_complete(self):
        for rec in self.cohort_ids.filtered(lambda tree_id : tree_id.tree_state in ['approved_pp', 'approved_p']):            
            date_begin, date_end = self.compute_season_period(self.date.year, rec.cpdm_tree_id.term)
            print(self.get_data_from_type(rec, rec.cpdm_tree_id.type, 'setting_id').id)
            print(self.get_data_from_type(rec, rec.cpdm_tree_id.type, 'site_id').id)
            archive_id = self.env["archive"].create({
                'student_id': rec.student_id.id,
                'site_id': self.get_data_from_type(rec, rec.cpdm_tree_id.type, 'site_id').id,
                'tree_id': rec.cpdm_tree_id.id,
                'cohort_id': rec.id,
                'date_begin': date_begin,
                'date_end': date_end,
                'setting_id': self.get_data_from_type(rec, rec.cpdm_tree_id.type, 'setting_id').id,
                'intership_period': rec.cpdm_tree_id.type,
            })
            rec.student_id.locatio_ids.write({
                'archive_id': archive_id.id,
                'active': False,
            })
            ttype = rec.cpdm_tree_id.type
            data = {}
            if ttype == 'ice':
                data = {'is_complete_ice': True}
            elif ttype == 'tce1':
                data = {'is_complete_tce1': True}
            elif ttype == 'tce2':
                data = {'is_complete_tce2': True}

            rec.student_id.write(data)
        self.write({
            'state': 'done',
        })
    
    def action_processing_by_bot(self):
        self.write({
            'is_bot': True,
        })
    
    @api.model
    def create(self, vals):
        if 'sequence_number' not in vals or vals.get('sequence_number', False) == False or vals['sequence_number'] == _('New'):
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('cpdm.tree') or _('New')
        return super(CPDMTree, self).create(vals)
    
    def compute_season_period(self, year, season):
        if season == 'summer':
            start_month = 6  # June
            end_month = 8  # August
        elif season == 'spring':
            start_month = 3  # March
            end_month = 5  # May
        elif season == 'fall':
            start_month = 9  # September
            end_month = 11  # November
        else:
            raise ValueError("Invalid season")

        start_date = datetime.date(year, start_month, 1)
        next_month = end_month + 1

        if next_month > 12:
            next_month = 1  # Wrap around to January of next year
            next_year = year + 1
        else:
            next_year = year

        end_date = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)

        return start_date, end_date
        
    # Cron job
    def check_end_date_to_update_status(self):
        cpdm_tree_ids = self.sudo().search([("state","=","running"),("date_end" ,"<",date.today())])
        cpdm_tree_ids.sudo().write({
            "state" : "done"
            })
    
    


class ClinicInfoGathering(models.Model):
    _name = 'clinic.info.gathering'
    _description = 'Clinic information Gathering'
    
    clinc_id = fields.Many2one('site', string='Clinc(site)')
    num_students = fields.Integer(string='Number of students')
    tree_id = fields.Many2one('cpdm.tree', string='Tree')
    state = fields.Selection(
        selection=[
            ('not_confirmed', 'Not Confirmed'),
            ('confirmed', 'Confirmed'),
            ],
        string='State', default='not_confirmed')
    is_confirmed_send = fields.Boolean(string='is Confirmation Send')
    setting_type = fields.Selection([
        ('ip', 'IP'),
        ('op', 'OP'),
    ], string='Setting Type',default='ip')
    date_end = fields.Datetime('End Date')
    contract_state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Contract State', group_expand='_expand_states', copy=False,
       tracking=True, help='Status of the contract', default='draft')

    @api.onchange('clinc_id')
    def _get_state(self):
        for rec in self:
            if rec.clinc_id:
                rec.contract_state = rec.clinc_id.contract_id.state or False
                rec.date_end = rec.clinc_id.contract_id.date_end or False

    def action_confirm(self):
        for rec in self:               
            if rec.tree_id.type == 'ice':
                rec.tree_id.cohort_ids.filtered(lambda x : x.ice_site_id.id == rec.clinc_id.id).write({
                    'ice_placement_status': 'done'
                })
            elif rec.tree_id.type == 'tce1':
                rec.tree_id.cohort_ids.filtered(lambda x : x.tce1_site_id.id == rec.clinc_id.id).write({
                    'tce1_placement_status': 'done'
                })
            elif rec.tree_id.type == 'tce2':
                rec.tree_id.cohort_ids.filtered(lambda x : x.tce2_site_id.id == rec.clinc_id.id).write({
                    'tce2_placement_status': 'done'
                })
        self.write({
                'state': 'confirmed'
            })
            
    
    def action_send_email_to_clinck(self):
        for rec in self:
            if rec.clinc_id.email:
                mail = (
                            self.env["mail.mail"]
                            .sudo()
                            .create(
                                {
                                    "subject": _("Test Request confirm Hardship"),
                                    "email_from": self.env.company.email,
                                    "body_html": "Dear :- {},<br/>Test to Click confirm  <br/><br/>Thank you,<br/>".format(
                                        rec.clinc_id.name
                                    ),
                                    "email_to": rec.clinc_id.email,
                                }
                            )
                            )
                mail.send()
                
                rec.is_confirmed_send = True
                if rec.tree_id.type == 'ice':
                    rec.tree_id.cohort_ids.filtered(lambda x : x.ice_site_id.id == rec.clinc_id.id).write({
                        'ice_placement_status': 'done'
                    })
                elif rec.tree_id.type == 'tce1':
                    rec.tree_id.cohort_ids.filtered(lambda x : x.tce1_site_id.id == rec.clinc_id.id).write({
                        'tce1_placement_status': 'done'
                    })
                elif rec.tree_id.type == 'tce2':
                    rec.tree_id.cohort_ids.filtered(lambda x : x.tce2_site_id.id == rec.clinc_id.id).write({
                        'tce2_placement_status': 'done'
                    })
                    
    def action_pending(self):
        for rec in self:               
            if rec.tree_id.type == 'ice':
                rec.tree_id.cohort_ids.filtered(lambda x : x.ice_site_id.id == rec.clinc_id.id).write({
                    'ice_placement_status': 'normal'
                })
            elif rec.tree_id.type == 'tce1':
                rec.tree_id.cohort_ids.filtered(lambda x : x.tce1_site_id.id == rec.clinc_id.id).write({
                    'tce1_placement_status': 'normal'
                })
            elif rec.tree_id.type == 'tce2':
                rec.tree_id.cohort_ids.filtered(lambda x : x.tce2_site_id.id == rec.clinc_id.id).write({
                    'tce2_placement_status': 'normal'
                })