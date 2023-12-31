# -*- coding: utf-8 -*-
from lxml import etree
import json
from odoo.exceptions import ValidationError

from odoo import models, fields, api, Command


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(1999, 2500)]

class PlacementRequest(models.Model):
    _name = 'placement.request'
    _inherit = ['mail.thread']
    _description = 'Placement Request'
    _rec_name = 'name'
    
    name = fields.Char(string='Name')
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students')
    offer_ids = fields.Many2many(comodel_name='placement.offer', string='offers')
    archive_offer_ids = fields.Many2many(comodel_name='archive.offer', string='archive offers')
    facility_ids = fields.Many2many('medical.facility', string='Medical Facilities')
    student_count = fields.Integer(compute='_compute_count')
    offer_count = fields.Integer(compute='_compute_count')
    archive_offer_count = fields.Integer(compute='_compute_count')
    facility_count = fields.Integer(compute='_compute_count')
    tree_ids = fields.One2many(comodel_name='tree.matching', inverse_name='request_id', string='Tree Matching')
    archive_ids = fields.One2many(comodel_name='archive', inverse_name='request_id', string='Tree Matching', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='state',default='draft')
    
    @api.depends('student_ids', 'offer_ids', 'facility_ids')
    def _compute_count(self):
        for request in self:
            request.student_count = len(request.student_ids)
            request.offer_count = len(request.offer_ids)
            request.facility_count = len(request.facility_ids)
            request.archive_offer_count = len(request.archive_offer_ids)
            
    # Filters
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce', 'TCE')
        ], string='Clinical Experience Type', default='ice', required=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Start Year', default='2000', required=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ], string='Start Term', default='fall', required=True)   

    
    apply_hardship = fields.Boolean(string='Apply Hardship Status', default=True)
    has_hardship = fields.Selection([
        ('no', 'No'),
        ('yes', 'Yes'),
    ], string='Has Hardship', default='no')
    
    # Setting Criteria
    apply_setting = fields.Boolean(string='Apply Setting', default=True)
    setting = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP'),
    ], string='Setting', default='op')
    
    # Location Criteria
    apply_location = fields.Boolean(string='Apply Distance', default=True, help="The chosen option will override the accepted distance to medical facilities.")
    
    def _get_default_distance(self):
        return float(self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')) or 50
    
    location_dist = fields.Float(string='Distance', default=_get_default_distance)
    
    # Placement Priority Criteria
    apply_placement_priority = fields.Boolean(string='Placement Priority', default=True)
    placement_priority = fields.Selection([
        ('no', 'No'),
        ('yes', 'Yes'),
        ], string='Has Placement Priority', default='yes',
        help="""
        Priority takeing
        1.ICE
            a. H.S ICE
            b. Student ICE
        2.TCE
            a. H.S TCE2
            b. Important Student no hase IP complete TCE2
            c. H.S TCE1
            d. Student TCE2
            e. Student TCE1
        """  
                                        )
    
    # Placement Status Criteria
    apply_placement_status = fields.Boolean(string='Apply Placement Status', default=True)
    placement_status = fields.Selection([
        ('not_placed', 'Not Placed'),
        ('matched', 'Matched'),
        ('approved', 'Approved'),
        ('pending', 'Pending'),
    ], default='not_placed', string='placement status')
    
    @api.model
    def convert_term_year(self, term, year):
        term_abbr = ""
        if term.lower() == "fall":
            term_abbr = "FA"
        elif term.lower() == "spring":
            term_abbr = "SP"
        elif term.lower() == "summer":
            term_abbr = "SU"

        year_abbr = str(year)[-2:]

        term_year = term_abbr + year_abbr

        return term_year
 
    
    @api.onchange('placement_type', 'placement_term', 'year', 'apply_hardship', 'has_hardship',
              'apply_setting', 'setting', 'apply_location', 'location_dist',
              'apply_placement_priority', 'placement_priority', 'apply_placement_status', 'placement_status')
    def _onchange_apply_criteria(self):
        self.ensure_one()
        term = self.convert_term_year(self.placement_term, self.year)
        student_ids, archive_offer_ids, location_dist = self.get_filter_data()
        
        print(student_ids)
        print('============================== All Student==================================')
        print("student_ids",student_ids)
        placement_status = ['confirmed', 'completed']
        
        if self.apply_placement_status and self.placement_status:
            placement_status = [self.placement_status]
            
        if self.placement_type == 'ice' and self.apply_placement_priority:
                if self.placement_priority == 'yes':
                    student_ids = student_ids.filtered(lambda student_id: student_id.is_with_hardship)
                else:
                    student_ids = student_ids.filtered(lambda student_id: not student_id.is_with_hardship)
                    
        if self.placement_type == 'tce' and self.apply_placement_priority:
            if self.placement_priority == 'yes':
                hardship_student_ids = student_ids.filtered(lambda student_id: student_id.is_with_hardship)
                remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', hardship_student_ids.ids), ('placement_status', 'in', placement_status)]).mapped('student_id')
                hardship_complete_tce2 = hardship_student_ids.filtered(lambda x: x.tce2_term == term) - remove_stu
                

                remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', student_ids.ids), ('placement_status', 'in', placement_status)]).mapped('student_id')
                important_student_complete_tce2 = student_ids.filtered(lambda x: x.tce2_term == term and not x.is_take_ip) - remove_stu
                # //*
                remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce1'), ('student_id', 'in', hardship_student_ids.ids), ('placement_status', 'in', placement_status)]).mapped('student_id')
                hardship_complete_tce1 = hardship_student_ids.filtered(lambda x: x.tce1_term == term) - remove_stu
                

                print('============================== TCE placement_priority YES==================================')
                print("hardship TCE2",hardship_complete_tce2)
                print("important TCE2",important_student_complete_tce2)
                print("Hardship TCE1",hardship_complete_tce1)
                student_ids = hardship_complete_tce2 + important_student_complete_tce2 + hardship_complete_tce1
            else:
                print('----------------------------------------------------------------',student_ids)
                remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', student_ids.ids), ('placement_status', 'not in', placement_status)]).mapped('student_id')
                student_complete_tce2 = student_ids.filtered(lambda x: x.tce2_term == term and x.is_take_ip) - remove_stu
                
                
                remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce1'), ('student_id', 'in', student_ids.ids), ('placement_status', 'not in', placement_status)]).mapped('student_id')
                print(remove_stu)
                student_complete_tce1 = student_ids.filtered(lambda x: x.tce1_term == term) - remove_stu
                print('============================== TCE placement_priority NO==================================')
                print("STUDENT TCE2",student_complete_tce2)
                print("STUDENT TCE1",student_complete_tce1)
                student_ids = student_complete_tce2 + student_complete_tce1
                
        
        self.student_ids = student_ids
        self.offer_ids = archive_offer_ids.mapped('offer_id')
        self.archive_offer_ids = archive_offer_ids
        self.facility_ids = archive_offer_ids.mapped('facility_id')  
        print(archive_offer_ids)
        
    def get_filter_data(self):
        student_domain = []
        location_dist = float(self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')) or 50
        
        term = self.convert_term_year(self.placement_term, self.year)
        
        offer_ids = self.env['placement.offer'].sudo().search([('state', '=', 'placementing'), ('placement_type', '=', self.placement_type), ('placement_term', '=', self.placement_term), ('year', '=', self.year)])
        archive_offer_ids = offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
        offer_ids = archive_offer_ids.mapped('offer_id')

        
        # Apply filter for placement_type
        if self.placement_type == 'ice':
            student_domain += [('ice_term', '=', term)]
            
        elif self.placement_type == 'tce':
            student_domain += ['|', ('tce1_term', '=', term), ('tce2_term', '=', term)]
                
        # Apply filter for has_hardship
        if self.apply_hardship and self.has_hardship:
            if self.has_hardship == 'yes':
                student_domain.append(('is_with_hardship', '=', True))
            else:
                student_domain.append(('is_with_hardship', '=', False))
        
        
        student_ids = self.env["res.partner"].sudo().search(student_domain).filtered(lambda x: len(x.geographical_ids) > 0)
        archive_ids = self.env['archive'].search([('student_id', 'in', student_ids.ids)])
        
        
        # Apply filter for placement_status
        if self.apply_placement_status and self.placement_status:
            archive_ids = archive_ids.filtered(lambda x:x.placement_status == self.placement_status)
            student_ids = archive_ids.mapped('student_id')
            placement_status = [self.placement_status]
            
        
        # Apply filter for setting
        if self.apply_setting and self.setting:
            archive_student_ids = self.env['archive'].search([('id', 'in', archive_ids.ids), ('student_id', 'in', student_ids.ids), ('setting', '=', 'ip'), ('placement_status', 'in', ['approved', 'confirmed', 'completed'])]).mapped('student_id')# TODO: Add Pending status for take it for match
            student_ids -= archive_student_ids
            if self.setting == 'op':
                archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.setting == 'op')

            else:
                archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.setting == 'ip')
                            
        
        # Apply filter for location_dist
        if self.apply_location and self.location_dist:
            location_dist = self.location_dist
        
        return student_ids, archive_offer_ids, location_dist
        
    def apply_filters(self):
        location_dist = float(self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')) or 50
        
        self._preparing_reapply_filter()
        # Apply filter for location_dist
        if self.apply_location and self.location_dist:
            location_dist = self.location_dist
            
        student_ids = self.student_ids
        archive_offer_ids = self.archive_offer_ids
        
        hardship_student_ids = student_ids.filtered(lambda student_id: student_id.is_with_hardship)
        student_ids -= hardship_student_ids
        
        if self.placement_type == 'ice':
            self.apply_ice(hardship_student_ids, student_ids, archive_offer_ids, location_dist)
        else:
            self.apply_tce(hardship_student_ids, student_ids, archive_offer_ids, location_dist)
        
            
    def apply_filter(self):
        self._preparing_reapply_filter()
        
        offer_ids = self.env['placement.offer'].sudo().search([('state', '=', 'placementing'), ('placement_type', '=', self.placement_type), ('placement_term', '=', self.placement_term), ('year', '=', self.year)])
        archive_offer_ids = offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
        facility_ids = archive_offer_ids.mapped('facility_id')
        offer_ids = archive_offer_ids.mapped('offer_id')
        print('******************************** INITAL INFO')
        print(offer_ids)
        print(archive_offer_ids)
        print(facility_ids)
        print()
        print('-----------------------------------')
        
        student_domain = [('id', '!=', False)]
        term = self.convert_term_year(self.placement_term, self.year)
        
        # STUDENT Filters 
        if self.placement_type == 'ice':
            student_domain += [('ice_term', '=', term)]
            
        elif self.placement_type == 'tce':
            student_domain += ['|', ('tce1_term', '=', term), ('tce2_term', '=', term)]
            
 
        student_ids = self.env["res.partner"].sudo().search(student_domain).filtered(lambda x: len(x.geographical_ids) > 0)
        
        hardship_student_ids = student_ids.filtered(lambda student_id: student_id.is_with_hardship)
        student_ids -= hardship_student_ids
        print('*********************= Student Detals=****************************')
        print('***************Domain', student_domain)
        print('***************All student', student_ids)
        print('***************Hardship Studen', hardship_student_ids)
        print('***************facility_ids', facility_ids)
        print('***************offer_ids', offer_ids)
        print('***************archive_offer_ids', archive_offer_ids)
        print('--------------------------------------------------------')

        if self.placement_type == 'ice':
            self.apply_ice(hardship_student_ids, student_ids, archive_offer_ids)
        else:
            self.apply_tce(hardship_student_ids, student_ids, facility_ids, offer_ids, archive_offer_ids)
            
        ###########################################

        if len(self.archive_ids) > 0 :
            self.write({
                'state': 'done',
            })
    
        
    def _preparing_reapply_filter(self):
        if self.archive_ids:
            # self.archive_ids.filtered(lambda x: x.match_state == False).write({'placement_status': 'not_placed'}) # TODO:Using form change lines state to not_placed 
            self.archive_ids.filtered(lambda x: x.match_state == False).unlink() # TODO:Using form remove lines without add to archived record 
            
    # Filter Methods
    #------------------------------------------------------------------------------
    def apply_ice(self, hardship_student_ids, student_ids, archive_offer_ids, location_dist):
        self._apply_ice(hardship_student_ids, archive_offer_ids, location_dist, 'The student was prioritized over ICE student: YES')
        self._apply_ice(student_ids, archive_offer_ids, location_dist, 'The student was prioritized over ICE student: No')
    
    def apply_tce(self, hardship_student_ids, student_ids, archive_offer_ids, location_dist):
            term = self.convert_term_year(self.placement_term, self.year)
            print(term, archive_offer_ids)
            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', hardship_student_ids.ids), ('placement_status', 'in', ['confirmed', 'completed'])]).mapped('student_id')
            hardship_complete_tce2 = hardship_student_ids.filtered(lambda x: x.tce2_term == term) - remove_stu
            

            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', student_ids.ids), ('placement_status', 'in', ['confirmed', 'completed'])]).mapped('student_id')
            important_student_complete_tce2 = student_ids.filtered(lambda x: x.tce2_term == term and not x.is_take_ip) - remove_stu
            # //*
            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce1'), ('student_id', 'in', hardship_student_ids.ids), ('placement_status', 'in', ['confirmed', 'completed'])]).mapped('student_id')
            hardship_complete_tce1 = hardship_student_ids.filtered(lambda x: x.tce1_term == term) - remove_stu
            
            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', student_ids.ids), ('placement_status', 'in', ['confirmed', 'completed'])]).mapped('student_id')
            student_complete_tce2 = student_ids.filtered(lambda x: x.tce2_term == term and x.is_take_ip) - remove_stu
            
            
            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce1'), ('student_id', 'in', student_ids.ids), ('placement_status', 'in', ['confirmed', 'completed'])]).mapped('student_id')
            student_complete_tce1 = student_ids.filtered(lambda x: x.tce1_term == term) - remove_stu
            
            print('============================== TCE ==================================')
            print("hardship TCE2",hardship_complete_tce2)
            print("important TCE2",important_student_complete_tce2)
            print("Hardship TCE1",hardship_complete_tce1)
            print("Student TCE2",student_complete_tce2)
            print("Student TCE1",student_complete_tce1)
            
            self._apply_tce2(hardship_complete_tce2, archive_offer_ids, location_dist,'The student was prioritized over TCE2 student: YES' )
            self._apply_tce2(important_student_complete_tce2, archive_offer_ids, location_dist, 'The student was prioritized over TCE1 student: YES')
            self._apply_tce1(hardship_complete_tce1, archive_offer_ids, location_dist, 'The student was prioritized over TCE2 student: YES')
            self._apply_tce2(student_complete_tce2, archive_offer_ids, location_dist, 'The student was prioritized over TCE2 student: No')
            self._apply_tce1(student_complete_tce1, archive_offer_ids, location_dist, 'The student was prioritized over TCE1 student: NO')
            
    def _apply_ice(self, student_ids, archive_offer_ids, location_dist, priority=''):
        for student_id in student_ids:
            student_archive = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_type', '=', 'ice'), ('placement_status', '!=', 'not_placed')])
            if student_archive:
                continue
            
            archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
            archive_offer_facility_ids = archive_offer_ids.mapped('facility_id')
            archive_offer_facility_ids = student_id.get_accepted_distance_facility(archive_offer_facility_ids, location_dist)

            if not archive_offer_facility_ids:
                continue

            ip_offers = archive_offer_ids.filtered(lambda x :x.setting == 'ip')
            op_offers = archive_offer_ids.filtered(lambda x :x.setting == 'op')
            

            archive_offer_id = False
            archive_offer_facility_id = False
            geographical_id = False
            if op_offers:
                hardship_facility_id, geographical_id = student_id.get_nearest_facility(op_offers.mapped('facility_id'))
                offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False and archive_offer_id.setting == 'op')[0]
                archive_offer_id = offer_id
                archive_offer_facility_id = offer_id.facility_id
                
            if ip_offers:
                if not student_id.is_take_ip and ip_offers:
                    hardship_facility_id, geographical_id = student_id.get_nearest_facility(ip_offers.mapped('facility_id'))
                    offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False  and archive_offer_id.setting == 'ip')[0]
                    archive_offer_id = offer_id
                    archive_offer_facility_id = offer_id.facility_id
                
            if archive_offer_id and archive_offer_facility_id:
                student_criteria, offer_criteria = self.get_student_matching_report(student_id, 'ICE', archive_offer_id.setting, geographical_id, archive_offer_facility_id, priority, location_dist)
                archive_id = self.env["archive"].create({
                        'student_id': student_id.id,
                        'facility_id': archive_offer_facility_id.id,
                        'student_criteria': student_criteria,
                        'offer_criteria': offer_criteria,
                        'placement_type': 'ice',
                        'setting': archive_offer_id.setting,
                        'placement_term': self.placement_term,
                        'year': self.year,
                        'geographical_id': geographical_id.id if geographical_id else False,
                        'archive_offer_id': archive_offer_id.id,
                        'request_id': self.id,
                    })
                archive_offer_id.student_id = student_id.id
                archive_offer_id.is_linked = True
                
    def _apply_tce1(self, student_ids, archive_offer_ids, location_dist, priority=''):
        for student_id in student_ids:
            student_archive = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_type', '=', 'tce1'), ('placement_status', '!=', 'not_placed')])
            if student_archive:
                continue
            
            archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
            archive_offer_facility_ids = archive_offer_ids.mapped('facility_id')

            
            check_facility_ids = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('facility_id', 'in', archive_offer_facility_ids.ids)]).mapped('facility_id')
            if check_facility_ids and not student_id.is_with_hardship:
                archive_offer_facility_ids -= check_facility_ids
            
            archive_offer_facility_ids = student_id.get_accepted_distance_facility(archive_offer_facility_ids)

            if not archive_offer_facility_ids:
                continue

            ip_offers = archive_offer_ids.filtered(lambda x :x.setting == 'ip')
            op_offers = archive_offer_ids.filtered(lambda x :x.setting == 'op')
            

            archive_offer_id = False
            archive_offer_facility_id = False
            geographical_id = False
            if op_offers:
                hardship_facility_id, geographical_id = student_id.get_nearest_facility(op_offers.mapped('facility_id'))
                offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False and archive_offer_id.setting == 'op')[0]
                archive_offer_id = offer_id
                archive_offer_facility_id = offer_id.facility_id
                
            if ip_offers:
                if not student_id.is_take_ip and ip_offers:
                    hardship_facility_id, geographical_id = student_id.get_nearest_facility(ip_offers.mapped('facility_id'))
                    offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False  and archive_offer_id.setting == 'ip')[0]
                    archive_offer_id = offer_id
                    archive_offer_facility_id = offer_id.facility_id
                
            if archive_offer_id and archive_offer_facility_id:
                student_criteria, offer_criteria = self.get_student_matching_report(student_id, 'TCE1', archive_offer_id.setting, geographical_id, archive_offer_facility_id, priority, location_dist)
                archive_id = self.env["archive"].create({
                        'student_id': student_id.id,
                        'facility_id': archive_offer_facility_id.id,
                        'offer_criteria': offer_criteria,
                        'student_criteria': student_criteria,
                        'placement_type': 'tce1',
                        'setting': archive_offer_id.setting,
                        'placement_term': self.placement_term,
                        'year': self.year,
                        'geographical_id': geographical_id.id if geographical_id else False,
                        'archive_offer_id': archive_offer_id.id,
                        'request_id': self.id,
                    })
                archive_offer_id.student_id = student_id.id
                archive_offer_id.is_linked = True
        
    def _apply_tce2(self, student_ids, archive_offer_ids, location_dist, priority=''):
        for student_id in student_ids:
            student_archive = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_type', '=', 'tce2'), ('placement_status', '!=', 'not_placed')])
            if student_archive:
                continue
                        
            archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
            
            archive_offer_facility_ids = archive_offer_ids.mapped('facility_id')
            
            check_facility_ids = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('facility_id', 'in', archive_offer_facility_ids.ids)]).mapped('facility_id')
            if check_facility_ids and not student_id.is_with_hardship:
                archive_offer_facility_ids -= check_facility_ids
            
            archive_offer_facility_ids = student_id.get_accepted_distance_facility(archive_offer_facility_ids, location_dist)

            if not archive_offer_facility_ids:
                continue

            ip_offers = archive_offer_ids.filtered(lambda x :x.setting == 'ip')
            op_offers = archive_offer_ids.filtered(lambda x :x.setting == 'op')
            
            check_ip = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('setting', '=', 'ip')])
            if not check_ip and not ip_offers:
                continue
            
            archive_offer_id = False
            archive_offer_facility_id = False
            geographical_id = False
            if op_offers:
                hardship_facility_id, geographical_id = student_id.get_nearest_facility(op_offers.mapped('facility_id'))
                offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False and archive_offer_id.setting == 'op')[0]
                archive_offer_id = offer_id
                archive_offer_facility_id = offer_id.facility_id
            
            if ip_offers:
                if not student_id.is_take_ip and ip_offers:
                    hardship_facility_id, geographical_id = student_id.get_nearest_facility(ip_offers.mapped('facility_id'))
                    offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False  and archive_offer_id.setting == 'ip')[0]
                    archive_offer_id = offer_id
                    archive_offer_facility_id = offer_id.facility_id
                else:
                    continue
                
            if archive_offer_id and archive_offer_facility_id:
                student_criteria, offer_criteria = self.get_student_matching_report(student_id, 'TCE1', archive_offer_id.setting, geographical_id, archive_offer_facility_id, priority, location_dist)
                archive_id = self.env["archive"].create({
                        'student_id': student_id.id,
                        'facility_id': archive_offer_facility_id.id,
                        'offer_criteria': offer_criteria,
                        'student_criteria': student_criteria,
                        'placement_type': 'tce2',
                        'setting': archive_offer_id.setting,
                        'placement_term': self.placement_term,
                        'year': self.year,
                        'geographical_id': geographical_id.id if geographical_id else False,
                        'archive_offer_id': archive_offer_id.id,
                        'request_id': self.id,
                    })
                archive_offer_id.student_id = student_id.id
                archive_offer_id.is_linked = True
    
    def get_student_matching_report(self, student_id, placement_type, setting, geographical_id, facility_id, priority, facility_distance_mel):
        facility_distance_mel = facility_distance_mel or float(self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')) or 50
        distance, dis_and_geo = geographical_id.get_distance_with_zip_code(facility_id.geographical_id)
        term = self.convert_term_year(self.placement_term, self.year)
        clinical_experience = dict(self._fields['placement_type'].selection).get(self.placement_type)
        
        ice = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('placement_type', '=', 'ice')], order='id ASC', limit=1)
        ice_setting = dict(ice._fields['setting'].selection).get(ice.setting) if ice else 'None'
        
        tce1 = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('placement_type', '=', 'tce1')], order='id ASC', limit=1)
        tce1_setting = dict(tce1._fields['setting'].selection).get(tce1.setting) if tce1 else 'None'
        
        tce2 = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('placement_type', '=', 'tce2')], order='id ASC', limit=1)
        tce2_setting = dict(tce2._fields['setting'].selection).get(tce2.setting) if tce2 else 'None'
        
        
        ice_status = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_type', '=', 'ice')], order='id ASC', limit=1)
        ice_status = dict(ice_status._fields['placement_status'].selection).get(ice_status.placement_status) if ice_status else ''
        
        tce1_status = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_type', '=', 'tce1')], order='id ASC', limit=1)
        tce1_status = dict(tce1_status._fields['placement_status'].selection).get(tce1_status.placement_status) if tce1_status else ''
        
        tce2_status = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_type', '=', 'tce2')], order='id ASC', limit=1)
        tce2_status = dict(tce2_status._fields['placement_status'].selection).get(tce2_status.placement_status) if tce2_status else ''
        
        
        student_criteria = f"""
            <ul>
                <li><strong>Term: </strong>{term}</li>
                <li><strong>Clinical experience Type: </strong>{placement_type}</li>
                <li><strong>Hardship Status: </strong>{'Yes' if student_id.is_with_hardship else 'No'}</li>
                <li><strong>Placement Priority: </strong> {str(priority)}</li>
                <li><strong>Setting: </strong>
                    <ul>
                        <li>ICE: {ice_setting}</li>
                        <li>TCE I: {tce1_setting}</li>
                        <li>TCE II: {tce2_setting}</li>
                    </ul>
                </li>
                <li><strong>Placement Status History:</strong>
                    <ul>
                        <li>ICE: {ice_status}</li>
                        <li>ICE: {tce1_status}</li>
                        <li>TCE II: {tce2_status}</li>
                    </ul>
                </li>
                <li><strong>Location ({facility_distance_mel} miles or less): </strong>{str(geographical_id.city)} {geographical_id.state} {geographical_id.zip_code} ({distance} Miles)</li>
            </ul>
        """
        
        facility_criteria = f"""
            <ul>
                <li><strong>Term: </strong> {term}</li>
                <li><strong>Clinical experience Type: </strong> {clinical_experience}</li>
                <li><strong>Setting: </strong>{setting}</li>
                <li><strong>Location: </strong> {facility_id.address or ''}, {facility_id.geographical_id.state} {facility_id.geographical_id.zip_code}</li>
            </ul>
        """
        
        return student_criteria, facility_criteria
    
    # Smart Button Action Methods
    #------------------------------------------------------------------------------
    def action_view_students(self):
        action = self.env.ref('clinical_decision_making.student_action').read()[0]
        action['domain'] = [('id', 'in', self.student_ids.ids)]
        action['context'] = {'create': False, 'delete': False}
        return action
    
    def action_view_lines(self):
        action = self.env.ref('clinical_decision_making.placement_offer_action').read()[0]
        action['domain'] = [('id', 'in', self.offer_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        return action
    
    def action_view_offer_lines(self):
        action = self.env.ref('clinical_decision_making.action_archive_offer').read()[0]
        action['domain'] = [('id', 'in', self.archive_offer_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        return action
    
    def action_view_facilities(self):
        action = self.env.ref('clinical_decision_making.medical_facility_action').read()[0]
        action['domain'] = [('id', 'in', self.facility_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        return action
    #------------------------------------------------------------------------------
    
    
    # Methods
    #------------------------------------------------------------------------------
    def action_post(self):
        self.ensure_one()
        self.write({
            'state': 'done',
        })
    
    #------------------------------------------------------------------------------
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, options=options)
        if view_type == 'form':
            doc = etree.fromstring(res['arch'])
            for field in self._fields:
                    print(field)
                    field_xpath = "//field[@name='%s']" % field
                    nodes = doc.xpath(field_xpath)
                    for node in nodes:
                        modifiers = json.loads(node.get('modifiers') or '{}')

                        modifiers['readonly'] = [['state', '=', 'done']]
                        node.set('modifiers', json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res