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
    facility_ids = fields.Many2many('medical.facility', string='Medical Facilities')
    student_count = fields.Integer(compute='_compute_count')
    offer_count = fields.Integer(compute='_compute_count')
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
            
    # Filters
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce', 'TCE')
        ], string='Clinical Experience Type', default='ice', required=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', default='2000', required=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ], string='Term', default='fall', required=True)   

    

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
 
    @api.onchange('placement_type', 'year', 'placement_term')
    def _onchange_placement_type(self):
        offer_ids = self.env["archive.offer"].sudo().search([('placement_term', '=', self.placement_term), ('placement_type', '=', self.placement_type), ('year', '=', self.year), ('is_linked', '=', False), ('student_id', '=', False)])
        facility_ids = offer_ids.mapped('facility_id')
        term = self.convert_term_year(self.placement_term, self.year)
        student_domain = []
        if self.placement_type == 'ice':
            student_domain += [('ice_term', '=', term)]
        elif self.placement_type == 'tce':
            student_domain += ['|', ('tce1_term', '=', term), ('tce2_term', '=', term)]
        student_ids = self.env["res.partner"].sudo().search(student_domain)
        
        self.student_ids = student_ids
        self.offer_ids = offer_ids.mapped('offer_id')
        self.facility_ids = facility_ids  
        
    # @api.onchange('student_ids', 'offer_ids', 'facility_ids')
    # def _onchange_filter_data(self):
    #     records = []
    #     student_ids = self.student_ids
    #     facility_ids = self.facility_ids
    #     offer_ids = self.offer_ids
    #     facility_ids = self.env['medical.facility'].sudo().search([('id', 'in', facility_ids.ids)])
    #     offer_ids = self.env['placement.offer'].sudo().search([('id', 'in', offer_ids.ids)])
    #     student_ids = self.env['res.partner'].sudo().search([('id', 'in', student_ids.ids)])

    #     hardship_student_ids = self.env['res.partner'].sudo().search([('id', 'in', student_ids.ids), ('is_with_hardship', '=', True)])
    #     student_ids -= hardship_student_ids
    #     self_id = self.ids
    #     self_id = self.env['placement.request'].sudo().search([('id', 'in', self_id)], limit=1)
    #     print('--------------------------------------------------------',self_id.tree_ids)
    #     self_id.write({
    #         'tree_ids': [Command.unlink(tree_id.id) for tree_id in self_id.tree_ids]
    #     })
    #     print('--------------------------------------------------------',self_id.tree_ids)
    #     for stu in hardship_student_ids:
    #         facility_ids = stu.get_accepted_distance_facility(facility_ids)
    #         print(facility_ids)
    #         facility_ids = self.env['medical.facility'].sudo().search([('id', 'in', facility_ids)])
    #         ar_facility_ids = self.env['archive'].sudo().search([('student_id', 'in', stu.ids), ('facility_id', 'in', facility_ids.ids)]).mapped('facility_id')
    #         facility_ids -= ar_facility_ids
    #         offer_ids = offer_ids.filtered(lambda x: x.facility_id.id in facility_ids.ids)
            
    #         if stu.is_take_ip:
    #             offer_ids = offer_ids.mapped('line_ids').filtered(lambda x: x.code == 'op').mapped('offer_id')
    #         if offer_ids:
    #             data = {
    #                 'student_id': stu.id,
    #                 'facility_id': offer_ids[0].facility_id.id,
    #                 'request_id': self_id.id,
    #             }
    #             print('--------------------------------1111',stu)
                
    #             records.append(data)
                
    #     for n_stu in student_ids:
    #         facility_ids = n_stu.get_accepted_distance_facility(facility_ids)
    #         facility_ids = self.env['medical.facility'].sudo().search([('id', 'in', facility_ids)])
    #         ar_facility_ids = self.env['archive'].sudo().search([('student_id', 'in', n_stu.ids), ('facility_id', 'in', facility_ids.ids)]).mapped('facility_id')
    #         facility_ids -= ar_facility_ids
    #         offer_ids = offer_ids.filtered(lambda x: x.facility_id.id in facility_ids.ids)
            
    #         if n_stu.is_take_ip:
    #             offer_ids = offer_ids.mapped('line_ids').filtered(lambda x: x.code == 'op').mapped('offer_id')
    #         if offer_ids:
    #             data = {
    #                 'student_id': n_stu.id,
    #                 'facility_id': offer_ids[0].facility_id.id,
    #                 'request_id': self_id.id,
    #             }
    #             print('--------------------------------2222',n_stu)
    #             records.append(data)
    #     print(records)
    #     for values in records:
    #         self.env['tree.matching'].create(values)
    #     print(self.tree_ids)
            
   
    def apply_filter(self):
        
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
    
    def apply_ice(self, hardship_student_ids, student_ids, archive_offer_ids):
        self._apply_ice(hardship_student_ids, archive_offer_ids, 'The student was prioritized over ICE student: YES')
        self._apply_ice(student_ids, archive_offer_ids, 'The student was prioritized over ICE student: YES')
            
            
    
    def apply_tce(self, hardship_student_ids, student_ids, facility_ids, offer_ids, archive_offer_ids):
            term = self.convert_term_year(self.placement_term, self.year)
            print(term)
            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', hardship_student_ids.ids), ('placement_status', '!=', 'not_placed')]).mapped('student_id')
            hardship_complete_tce2 = hardship_student_ids.filtered(lambda x: x.tce2_term == term) - remove_stu
            

            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', student_ids.ids), ('placement_status', '!=', 'not_placed')]).mapped('student_id')
            important_student_complete_tce2 = student_ids.filtered(lambda x: x.tce2_term == term and not x.is_take_ip) - remove_stu
            # //*
            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce1'), ('student_id', 'in', hardship_student_ids.ids), ('placement_status', '!=', 'not_placed')]).mapped('student_id')
            hardship_complete_tce1 = hardship_student_ids.filtered(lambda x: x.tce1_term == term) - remove_stu
            
            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce2'), ('student_id', 'in', student_ids.ids), ('placement_status', '!=', 'not_placed')]).mapped('student_id')
            student_complete_tce2 = student_ids.filtered(lambda x: x.tce2_term == term and x.is_take_ip) - remove_stu
            
            
            remove_stu = self.env['archive'].search([ ('placement_type', '=', 'tce1'), ('student_id', 'in', student_ids.ids), ('placement_status', '!=', 'not_placed')]).mapped('student_id')
            student_complete_tce1 = student_ids.filtered(lambda x: x.tce1_term == term) - remove_stu
            
            print('============================== TCE ==================================')
            print("hardship TCE2",hardship_complete_tce2)
            print("important TCE2",important_student_complete_tce2)
            print("Hardship TCE1",hardship_complete_tce1)
            print("Student TCE2",student_complete_tce2)
            print("Student TCE1",student_complete_tce1)
            
            self._apply_tce2(hardship_complete_tce2, archive_offer_ids, 'The student was prioritized over TCE2 student: YES')
            self._apply_tce2(important_student_complete_tce2, archive_offer_ids, 'The student was prioritized over TCE1 student: YES')
            self._apply_tce1(hardship_complete_tce1, archive_offer_ids, 'The student was prioritized over TCE2 student: YES')
            self._apply_tce2(student_complete_tce2, archive_offer_ids, 'The student was prioritized over TCE2 student: No')
            self._apply_tce1(student_complete_tce1, archive_offer_ids, 'The student was prioritized over TCE1 student: NO')
            
    
    def _apply_ice(self, student_ids, archive_offer_ids, priority=''):
        for student_id in student_ids:
            student_archive = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_type', '=', 'ice'), ('placement_status', '!=', 'not_placed')])
            if student_archive:
                continue
            
            archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
            archive_offer_facility_ids = archive_offer_ids.mapped('facility_id')
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
                criteria = self.get_student_matching_report(student_id, 'ICE', archive_offer_id.setting, geographical_id, archive_offer_facility_id, priority)
                archive_id = self.env["archive"].create({
                        'student_id': student_id.id,
                        'facility_id': archive_offer_facility_id.id,
                        'criteria': criteria,
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
                
    def _apply_tce1(self, student_ids, archive_offer_ids, priority=''):
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
                criteria = self.get_student_matching_report(student_id, 'TCE1', archive_offer_id.setting, geographical_id, archive_offer_facility_id, priority)
                archive_id = self.env["archive"].create({
                        'student_id': student_id.id,
                        'facility_id': archive_offer_facility_id.id,
                        'criteria': criteria,
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
        
    def _apply_tce2(self, student_ids, archive_offer_ids, priority=''):
        for student_id in student_ids:
            student_archive = self.env['archive'].sudo().search([('student_id', '=', student_id.id), ('placement_type', '=', 'tce2'), ('placement_status', '!=', 'not_placed')])
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
                criteria = self.get_student_matching_report(student_id, 'TCE2', archive_offer_id.setting, geographical_id, archive_offer_facility_id, priority)
                archive_id = self.env["archive"].create({
                        'student_id': student_id.id,
                        'facility_id': archive_offer_facility_id.id,
                        'criteria': criteria,
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
    
    def get_student_matching_report(self, student_id, placement_type, setting, geographical_id, facility_id, priority):
        facility_distance_mel = float(self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')) or 50
        distance, dis_and_geo = geographical_id.get_distance_with_zip_code(facility_id.geographical_id)
        term = self.convert_term_year(self.placement_term, self.year)
        clinical_experience = self.placement_type
        
        ice = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('placement_type', '=', 'ice')], order='id ASC', limit=1)
        ice_setting = ice.setting if ice else 'None'
        
        tce1 = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('placement_type', '=', 'tce1')], order='id ASC', limit=1)
        tce1_setting = tce1.setting if tce1 else 'None'
        
        tce2 = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_status', '!=', 'not_placed'), ('placement_type', '=', 'tce2')], order='id ASC', limit=1)
        tce2_setting = tce2.setting if tce2 else 'None'
        
        
        ice_status = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_type', '=', 'ice')], order='id ASC', limit=1)
        ice_status = ice_status.placement_status if ice_status else ''
        
        tce1_status = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_type', '=', 'tce1')], order='id ASC', limit=1)
        tce1_status = tce1_status.placement_status if tce1_status else ''
        
        tce2_status = self.env['archive'].search([('student_id', '=', student_id.id), ('placement_type', '=', 'tce2')], order='id ASC', limit=1)
        tce2_status = tce2_status.placement_status if tce2_status else ''
        
        
        criteria = f"""
            <ul>
                <li><strong>Term: </strong> {term} ↦ {term}</li>
                <li><strong>Clinical experience Type: </strong> {clinical_experience} ↦ {placement_type}</li>
                <li><strong>Hardship Status: </strong>{'Yes' if student_id.is_with_hardship else 'No'}</li>
                <li><strong>Placement Priority: </strong> {str(priority)}</li>
                <li><strong>Setting: </strong>{setting} ↦ 
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
                <li><strong>Location ({facility_distance_mel} miles or less): </strong> {facility_id.address or ''}, {facility_id.geographical_id.state} {facility_id.geographical_id.zip_code} ↦ {str(geographical_id.city)} {geographical_id.state} {geographical_id.zip_code} {distance}</li>
            </ul>
        """
        return criteria
    
    # Smart Button Action Methods
    def action_view_students(self):
        action = self.env.ref('clinical_decision_making.student_action').read()[0]
        action['domain'] = [('id', 'in', self.student_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        return action
    
    def action_view_lines(self):
        action = self.env.ref('clinical_decision_making.placement_offer_action').read()[0]
        action['domain'] = [('id', 'in', self.offer_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        return action
    
    def action_view_facilities(self):
        action = self.env.ref('clinical_decision_making.medical_facility_action').read()[0]
        action['domain'] = [('id', 'in', self.facility_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        return action
    
    
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