# -*- coding: utf-8 -*-
from lxml import etree
import json
from odoo.exceptions import ValidationError

from odoo import models, fields, api, Command


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]

class PlacementRequest(models.Model):
    _name = 'placement.request'
    _inherit = ['mail.thread']
    _description = 'Placement Request'
    _rec_name = 'name'
    
    name = fields.Char(string='Round #')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students')
    offer_ids = fields.Many2many(comodel_name='placement.offer', string='offers')
    archive_offer_ids = fields.Many2many(comodel_name='archive.offer', string='archive offers', check_company=True)
    facility_ids = fields.Many2many('medical.facility', string='Medical Facilities')
    department_ids = fields.Many2many('facility.department', string='Department', check_company=True)    
    student_count = fields.Integer(compute='_compute_count')
    offer_count = fields.Integer(compute='_compute_count')
    archive_offer_count = fields.Integer(compute='_compute_count')
    facility_count = fields.Integer(compute='_compute_count')
    department_count = fields.Integer(compute='_compute_count')
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
            request.department_count = len(request.department_ids)
            request.archive_offer_count = len(request.archive_offer_ids)
            
    # Filters
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience', domain="[('company_id', '=', company_id)]", required=True, check_company=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', default='2000', required=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ], string='Term', default='fall', required=True)   

    
    apply_hardship = fields.Boolean(string='Apply Hardship Status', default=True)
    
    # Setting Criteria
    apply_setting = fields.Boolean(string='IP Setting Met ?', default=True)
    
    # Location Criteria
    apply_location = fields.Boolean(string='Apply Distance', default=True, help="The chosen option will override the accepted distance to medical facilities.")
    
    def _get_default_distance(self):
        return self.env.company.clinical_distance_mel or 50
    
    location_dist = fields.Float(string='Distance', default=_get_default_distance)
    
    # Placement Priority Criteria
    apply_placement_priority = fields.Boolean(string='Placement Priority', default=True,        
        help="""
            Priority takeing
                a. H.S Last Term Student
                b. Important Student no hase IP complete Last Term
                c. Normal Student With H.S
        """  
        )
    
    # Placement Status Criteria
    placement_status = fields.Selection([
        ('not_placed', 'Not Placed'),
        ('matched', 'Matched'),
        ('declined', 'Declined'),
        ('approved', 'Approved'),
        ('pending', 'Pending'),
    ], string='Placement Status')
    
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
 
    
    @api.onchange('experience_id', 'placement_term', 'year', 'apply_hardship',
              'apply_setting', 'apply_location', 'location_dist',
              'apply_placement_priority', 'placement_status')
    def _onchange_apply_criteria(self):
        self.ensure_one()
        term = self.convert_term_year(self.placement_term, self.year)
        student_ids, archive_offer_ids, location_dist = self.get_filter_data()
            
        print('============================== All Student==================================')
        print("student_ids",student_ids)
        print("self.experience_id",self.experience_id.name)
        
        
        # Apply filter for location_dist
        if self.apply_location and self.location_dist:
            location_dist = self.location_dist
            facility_ids = archive_offer_ids.mapped('facility_id')
            stud_ids = []
            for student_id in student_ids:
                accepted_facility_ids = student_id.get_accepted_distance_facility(facility_ids, location_dist)
                if not accepted_facility_ids:
                    stud_ids.append(student_id.id)
            student_ids -= self.env['res.partner'].sudo().search([('id', 'in', stud_ids)])
        
        if self.placement_status:
            domain = [('experience_id', '=', self.experience_id.id)]
            
            if self.placement_status == 'not_placed':
                has_no_archide = self.env['archive'].search(domain + [('student_id', 'in', student_ids.ids)]).mapped('student_id')
                has_no_archide = student_ids - has_no_archide
                notplaced_archide = self.env['archive'].search(domain + [('student_id', 'in', student_ids.ids), ('placement_status', 'in', ['not_placed']), ('placement_status', 'not in', ['matched', 'pending', 'confirmed', 'completed', 'approved'])]).mapped('student_id')
                student_ids = has_no_archide + notplaced_archide
            else:
                not_placement_stu = self.env['archive'].search(domain + [('student_id', 'in', student_ids.ids), ('placement_status', '=', self.placement_status)]).mapped('student_id')
                student_ids = not_placement_stu
             
        placement_status = ['matched', 'pending', 'confirmed', 'completed', 'approved'] # TODO: Here to Control the Student Avalivle 

        if self.apply_placement_priority:
            
                hardship_student_ids = student_ids.filtered(lambda student_id: student_id.is_with_hardship)
                last_experience_student = student_ids.filtered(lambda student_id: student_id.get_student_last_experience() == self.experience_id) 
                last_experience_student = last_experience_student.filtered(lambda student_id: not student_id.is_take_ip)
                last_experience_student -= hardship_student_ids
                
                print('==============================  placement_priority YES==================================')
                print("hardship Student",last_experience_student)
                print("important Student no has IP with last Term",hardship_student_ids)
                student_ids = last_experience_student + hardship_student_ids

                
        
        self.student_ids = student_ids
        self.offer_ids = archive_offer_ids.mapped('offer_id')
        self.archive_offer_ids = archive_offer_ids
        self.facility_ids = archive_offer_ids.mapped('facility_id')  
        
    def get_filter_data(self):
        student_domain = []
        location_dist = self.env.company.clinical_distance_mel or 50
        
        term = self.convert_term_year(self.placement_term, self.year)
        
        offer_ids = self.env['placement.offer.line'].sudo().search([('company_id', '=', self.company_id.id), ('parent_state', '=', 'offer_still_available'), ('experience_id', '=', self.experience_id.id), ('placement_term', '=', self.placement_term), ('year', '=', self.year)])
        facility_ids = offer_ids.mapped('facility_id').filtered(lambda x : x.contract_id.state in ['open', 'require_renewal'])
        offer_ids = offer_ids.filtered(lambda offer_id: offer_id.facility_id.id in facility_ids.ids)
        archive_offer_ids = offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
        offer_ids = archive_offer_ids.mapped('offer_id')        
   
        # Apply filter for has_hardship
        if self.apply_hardship:
                student_domain.append(('is_with_hardship', '=', True))
        student_ids = self.env["res.partner"].sudo().search(student_domain).filtered(lambda x: len(x.geographical_ids) > 0)
        student_ids = student_ids.mapped('experience_schedual_ids').filtered(lambda x: x.name == term and x.experience_id.id == self.experience_id.id).mapped('student_id')

        rem_stu_ids = self.env['archive'].search([('student_id', 'in', student_ids.ids), ('placement_status', 'in', ['confirmed', 'completed']), ('year', '=', self.year), ('placement_term', '=', self.placement_term)]).mapped('student_id') # TODO: Add 'approved',  here 
        student_ids -= rem_stu_ids
            
        archive_ids = self.env['archive'].search([('student_id', 'in', student_ids.ids), ('placement_status', 'in', ['confirmed', 'completed'])])# TODO: Add 'approved',  here 
        
        # ------------------------------------------------------------------
        # Apply filter for setting
        if self.apply_setting:
            met_student_ids = self.env['archive'].search([('id', 'in', archive_ids.ids), ('student_id', 'in', student_ids.ids), ('setting', '=', 'ip'), ('placement_status', 'in', ['confirmed', 'completed'])]).mapped('student_id')# TODO: Add Pending status for take it for match # TODO: Add 'approved',  here 
            student_ids = met_student_ids
            archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.setting == 'op')

        # Apply filter for location_dist
        if self.apply_location and self.location_dist:
            location_dist = self.location_dist
        
        return student_ids, archive_offer_ids, location_dist
        
    def apply_filters(self):
        print(self.env.context)
        location_dist = self.env.company.clinical_distance_mel or 50
        
        # Apply filter for location_dist
        if self.apply_location and self.location_dist:
            location_dist = self.location_dist
            
        student_ids = self.student_ids
        archive_offer_ids = self.archive_offer_ids
        
        hardship_student_ids = student_ids.filtered(lambda student_id: student_id.is_with_hardship)
        student_ids -= hardship_student_ids
        
        
        if self.placement_status:
            self.get_placement_status_archive_filter()
        
        print('... ... ...')
        self.apply_experience(hardship_student_ids, student_ids, archive_offer_ids, location_dist)

        self._onchange_apply_criteria()
    
    def get_placement_status_archive_filter(self):
        print('------------------------------Apply Plcement Status Archide for ', self.student_ids)
        domain = [('experience_id', '=', self.experience_id.id)]
        co_student_ids = self.student_ids - self.env['archive'].search(domain + [('student_id', 'in', self.student_ids.ids), ('placement_status', 'in', ['confirmed', 'completed'])]).mapped('student_id')
        archive_ids = self.env['archive'].search([('student_id', 'in', co_student_ids.ids), ('placement_status', '=', self.placement_status)])
        archive_ids.write({
            'placement_status': 'not_placed'
        })
            

    
    # Filter Methods
    #------------------------------------------------------------------------------
    def apply_experience(self, hardship_student_ids, student_ids, archive_offer_ids, location_dist):
        hardship_last_experience_student = hardship_student_ids.filtered(lambda student_id: student_id.get_student_last_experience() == self.experience_id)
        last_experience_student = student_ids.filtered(lambda student_id: student_id.get_student_last_experience() == self.experience_id) 
        
        hardship_student_ids -= hardship_last_experience_student
        student_ids -= last_experience_student

        if hardship_last_experience_student or last_experience_student:
            self._apply_experience(hardship_last_experience_student, archive_offer_ids, location_dist, 'The student was prioritized over %s student: YES' % self.experience_id.name)
            self._apply_experience(last_experience_student.filtered(lambda student_id: not student_id.is_take_ip), archive_offer_ids, location_dist, 'The student was prioritized over %s student: YES' % self.experience_id.name)
            self._apply_experience(last_experience_student.filtered(lambda student_id: student_id.is_take_ip), archive_offer_ids, location_dist, 'The student was prioritized over %s student: NO' % self.experience_id.name)
        
        if hardship_student_ids or student_ids:
            self._apply_experience(hardship_student_ids, archive_offer_ids, location_dist, 'The student was prioritized over %s student: YES' % self.experience_id.name)
            self._apply_experience(student_ids, archive_offer_ids, location_dist, 'The student was prioritized over %s student: No' % self.experience_id.name)

 
    def _apply_experience(self, student_ids, archive_offer_ids, location_dist, priority=''):
        for student_id in student_ids:
            allow_offers =  archive_offer_ids.mapped('offer_id')
            for x in archive_offer_ids.mapped('offer_id'):
                if student_id.id in x.blocked_ids.ids:
                    allow_offers -= x
            archive_offer_ids = archive_offer_ids.filtered(lambda x: x.offer_id.id in  allow_offers.ids)
            
            # student_archive = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_type', '=', 'ice'), ('placement_status', '!=', 'not_placed')])
            # if student_archive:
            #     continue
            
            archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
            archive_offer_department_ids = archive_offer_ids.mapped('department_id')
            archive_offer_department_ids = student_id.get_accepted_distance_facility(archive_offer_department_ids, location_dist)
            if not archive_offer_department_ids:
                continue

            ip_offers = archive_offer_ids.filtered(lambda x :x.setting == 'ip')
            op_offers = archive_offer_ids.filtered(lambda x :x.setting == 'op')
            

            archive_offer_id = False
            archive_offer_department_id = False
            geographical_id = False
            if op_offers:
                hardship_department_id, geographical_id = student_id.get_nearest_facility(op_offers.mapped('department_id'))
                offer_id = hardship_department_id.archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False and archive_offer_id.setting == 'op')[0]
                archive_offer_id = offer_id
                archive_offer_department_id = offer_id.department_id
                
            if ip_offers:
                if not student_id.is_take_ip and ip_offers:
                    hardship_department_id, geographical_id = student_id.get_nearest_facility(ip_offers.mapped('department_id'))
                    offer_id = hardship_department_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False  and archive_offer_id.setting == 'ip')[0]
                    archive_offer_id = offer_id
                    archive_offer_department_id = offer_id.department_id
            
            if archive_offer_id and archive_offer_department_id:
                student_criteria, offer_criteria = self.get_student_matching_report(student_id, 'Matched', archive_offer_id.setting, geographical_id, archive_offer_department_id, priority, location_dist)
                archive_id = self.env["archive"].create({
                        'student_id': student_id.id,
                        'department_id': archive_offer_department_id.id,
                        'student_criteria': student_criteria,
                        'offer_criteria': offer_criteria,
                        'experience_id': self.experience_id.id,
                        'setting': archive_offer_id.setting,
                        'placement_term': self.placement_term,
                        'year': self.year,
                        'geographical_id': geographical_id.id if geographical_id else False,
                        'archive_offer_id': archive_offer_id.id,
                        'request_id': self.id,
                    })
                archive_offer_id.student_id = student_id.id
                archive_offer_id.is_linked = True
                

    def get_student_matching_report(self, student_id, placement_status, setting, geographical_id, department_id, priority, facility_distance_mel):
        facility_distance_mel = facility_distance_mel or self.env.company.clinical_distance_mel or 50
        distance, dis_and_geo = geographical_id.get_distance_with_zip_code(department_id.geographical_id)
        term = self.convert_term_year(self.placement_term, self.year)
        
        experience_ids = self.env['clinical.experience'].search([('company_id', '=', student_id.company_id.id)])
        setting_report = ""
        status_report = ""
        setting = 'IP' if setting == 'ip' else 'OP' if setting == 'op' else ''
        for experience_id in experience_ids:
            experience = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('experience_id', '=', experience_id.id)], order='id ASC', limit=1)
            experience_setting = dict(experience._fields['setting'].selection).get(experience.setting) if experience else 'None'
            experience_status = self.env['archive'].search([('student_id', '=', student_id.id), ('experience_id', '=', experience_id.id)], order='id ASC', limit=1)
            experience_status = dict(experience_status._fields['placement_status'].selection).get(experience_status.placement_status) if experience_status else 'Not Placed'
            if experience_id.id == self.experience_id.id:
                setting_report += f"<li>{experience_id.name}: {setting}</li>"
                status_report += f"<li>{experience_id.name}: {placement_status}</li>"
            else:
                setting_report += f"<li>{experience_id.name}: {experience_setting}</li>"
                status_report += f"<li>{experience_id.name}: {experience_status}</li>"
                
        
        
        student_criteria = f"""
            <ul>
                <li><strong>Term: </strong>{term}</li>
                <li><strong>Clinical Experience : </strong>{self.experience_id.name}</li>
                <li><strong>Hardship Status: </strong>{'Yes' if student_id.is_with_hardship else 'No'}</li>
                <li><strong>Placement Priority: </strong> {str(priority)}</li>
                <li><strong>Setting: </strong>
                    <ul>
                        {setting_report}
                    </ul>
                </li>
                <li><strong>Placement Status History:</strong>
                    <ul>
                        {status_report}
                    </ul>
                </li>
                <li><strong>Location ({facility_distance_mel} miles or less): </strong>{str(geographical_id.city)} {geographical_id.state} {geographical_id.zip_code} ({round(distance, 2)} Miles)</li>
            </ul>
        """
        
        facility_criteria = f"""
            <ul>
                <li><strong>Term: </strong> {term}</li>
                <li><strong>Clinical experience : </strong> {self.experience_id.name}</li>
                <li><strong>Setting: </strong>{setting}</li>
                <li><strong>Location: </strong> {str(department_id.street) + ', ' if department_id.street else ''} {department_id.geographical_id.state} {department_id.geographical_id.zip_code}</li>
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
        action['domain'] = [('id', 'in', self.archive_offer_ids.ids), ('active', '=', True)]
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
