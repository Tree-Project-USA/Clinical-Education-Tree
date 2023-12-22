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
        ], string='Type', default='ice', required=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', default='2000', required=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ], string='Term', default='fall', required=True)   
    filter_by_hardship = fields.Boolean(string='Filter by Hardship')
    placement_offer_id = fields.Many2one(comodel_name='placement.offer', string='Offer')
    program_id = fields.Many2one(comodel_name='program', string='Program')
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', domain=[('is_student', '=', True)])
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Facility')
    code = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP'),
    ], string='Code')
    

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
 
    @api.onchange('placement_type', 'year', 'placement_term', 'filter_by_hardship', 'program_id', 'student_id', 'facility_id')
    def _onchange_placement_type(self):
        offer_ids = self.env["placement.offer"].sudo().search([('state', '=', 'progress')])
        facility_ids = offer_ids.mapped('facility_id')

        term = self.convert_term_year(self.placement_term, self.year)

        student_domain = [('id', '!=', False)]
        offer_domain = [('state', '=', 'progress')]
        facility_domain = [('id', '!=', False)]

        if self.placement_type == 'ice':
            student_domain += [('ice_term', '=', term)]
        elif self.placement_type == 'tce':
            student_domain += ['|', ('tce1_term', '=', term), ('tce2_term', '=', term)]

        if self.filter_by_hardship:
            student_domain += [('is_with_hardship', '=', True)]

        if self.program_id:
            student_domain += [('program_id', '=', self.program_id.id)]

        if self.student_id:
            student_domain += [('id', '=', self.student_id.id)]

        student_ids = self.env["res.partner"].sudo().search(student_domain)
        hardship_student_ids = student_ids.filtered(lambda x: x.is_with_hardship)
        student_ids -= hardship_student_ids

        if self.code and self.code == 'ip':
            student_ids = student_ids.filtered(lambda x: not x.is_take_ip)

        if self.facility_id:
            facility_domain += [('id', '=', self.facility_id.id)]
            if self.code:
                offer_ids = offer_ids.filtered(lambda x: x.facility_id.id == self.facility_id.id)
            student_ids -= self.env['archive'].sudo().search([('student_id', 'in', student_ids.ids), ('facility_id', '=', self.facility_id.id)]).mapped('student_id')

        offer_domain += [('line_ids.code', '=', self.code)] if self.code else []
        offer_ids = offer_ids.filtered_domain(offer_domain).mapped('line_ids.offer_id')

        facility_ids = self.env["medical.facility"].sudo().search(facility_domain)

        self.student_ids = student_ids + hardship_student_ids
        self.offer_ids = offer_ids
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
        archive_offer_ids = offer_ids.mapped('archive_offer_ids')
        archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
        # offer_ids = offer_ids.mapped('offer_id')
        facility_ids = offer_ids.mapped('facility_id')
        
        
        student_domain = [('id', '!=', False)]
        facility_domain = [('id', '!=', False)]
        term = self.convert_term_year(self.placement_term, self.year)
        
        # STUDENT Filters 
        if self.placement_type == 'ice':
            student_domain += [('ice_term', '=', term)]
            
        elif self.placement_type == 'tce':
            student_domain += ['|', ('tce1_term', '=', term), ('tce2_term', '=', term)]
            
        if self.filter_by_hardship:
            student_domain += [('is_with_hardship', '=', True)]

        if self.program_id:
            student_domain += [('program_id', '=', self.program_id.id)]

        if self.student_id:
            student_domain += [('id', '=', self.student_id.id)]

        print(student_domain)
        student_ids = self.env["res.partner"].sudo().search(student_domain).filtered(lambda x: len(x.geographical_ids) > 0)
        # if self.placement_type == 'ice':
        #     student_ids = student_ids.filtered(lambda x: x.is_complete_ice == False)
        # elif self.placement_type == 'tce':...
            
        # is_complete_tce1 = student_ids.filtered(lambda x: x.is_complete_tce1)
        # is_complete_tce2 = student_ids.filtered(lambda x: x.is_complete_tce2)
        hardship_student_ids = student_ids.filtered(lambda x: x.is_with_hardship)
        student_ids -= hardship_student_ids
        
        ###########################################

        if self.code and self.code == 'ip':
            student_ids = student_ids.filtered(lambda x: not x.is_take_ip)
            hardship_student_ids = hardship_student_ids.filtered(lambda x: not x.is_take_ip)
        
        # Facility Filters        
        if self.facility_id:
            facility_domain += [('id', '=', self.facility_id.id)]
            if self.code:
                offer_ids = offer_ids.filtered(lambda x: x.facility_id.id == self.facility_id.id)
                
            student_ids -= self.env['archive'].sudo().search([('student_id', 'in', student_ids.ids), ('facility_id', '=', self.facility_id.id)]).mapped('student_id')
            hardship_student_ids -= self.env['archive'].sudo().search([('student_id', 'in', hardship_student_ids.ids), ('facility_id', '=', self.facility_id.id)]).mapped('student_id')

        facility_ids = offer_ids.mapped('facility_id')
        archive_offer_ids = offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)


        records = []
        self.student_ids = student_ids
        self.facility_ids = facility_ids
        self.offer_ids = offer_ids

        # unlimke Reov
        # print('--------------------------------------------------------',self_id.tree_ids)
        # self_id.write({
        #     'tree_ids': [Command.unlink(tree_id.id) for tree_id in self_id.tree_ids]
        # })
        # print('--------------------------------------------------------',self_id.tree_ids)
        
        for hardship_student_id in hardship_student_ids:
            
                archive_offer_ids -= archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
                archive_offer_facility_ids = archive_offer_ids.mapped('facility_id')
                archive_offer_facility_ids -= self.env['archive'].sudo().search([('student_id', '=', hardship_student_id.id), ('facility_id', 'in', archive_offer_facility_ids.ids), ('placement_status', 'in', ['approved', 'completed', 'pending'])]).mapped('facility_id')
                
                
                ip_offers = archive_offer_ids.filtered(lambda x :x.setting == 'ip')
                op_offers = archive_offer_ids.filtered(lambda x :x.setting == 'op')
                s = False
                s_f = False
                if op_offers:
                    s=op_offers[0]
                    s_f=op_offers[0].facility_id
                    
                if ip_offers:
                    if not hardship_student_id.is_take_ip and ip_offers:
                        hardship_facility_id = hardship_student_id.get_nearest_facility(ip_offers.mapped('facility_id'))
                        offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)[0]
                        s = offer_id
                        s_f=offer_id.facility_id
                    
                if not hardship_student_id.is_take_ip and ip_offers:
                    hardship_facility_id = hardship_student_id.get_nearest_facility(ip_offers.mapped('facility_id'))
                    offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)[0]
                    s = offer_id
                    s_f=offer_id.facility_id
                type_tce1 = self.env['archive'].sudo().search([('student_id', '=', hardship_student_id.id), ('facility_id', '=', s_f.id), ('state', 'in', ['approved', 'completed']), ('placement_type', '=', 'tce1')])
                archive_id = self.env["archive"].create({
                        'student_id': hardship_student_id.id,
                        'facility_id': s_f.id,
                        'placement_type': 'ice' if self.placement_type == 'ice' else 'tce2' if type_tce1 else 'tce1',
                        'setting': self.code,
                        'placement_term': self.placement_term,
                        'year': self.year,
                        'archive_offer_id': s.id,
                        'request_id': self.id,
                    })
                s.is_linked = True
            
                    # print('--------------------------------1111',stu)

        for n_stu in student_ids:
                archive_offer_ids = archive_offer_ids.filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)
                archive_offer_facility_ids = archive_offer_ids.mapped('facility_id')
                print(archive_offer_facility_ids)
                archive_offer_facility_ids -= self.env['archive'].sudo().search([('student_id', '=', n_stu.id), ('facility_id', 'in', archive_offer_facility_ids.ids), ('placement_status', 'in', ['approved', 'completed', 'pending'])]).mapped('facility_id')
                
                ip_offers = archive_offer_ids.filtered(lambda x :x.setting == 'ip')
                op_offers = archive_offer_ids.filtered(lambda x :x.setting == 'op')
                s = False
                s_f = False
                if op_offers:
                    print(op_offers)
                    s=op_offers[0]
                    s_f=op_offers[0].facility_id
                    
                ip_offers = archive_offer_ids.filtered(lambda x :x.setting == 'ip')
                op_offers = archive_offer_ids.filtered(lambda x :x.setting == 'op')
                s = False
                s_f = False
                if op_offers:
                    print(op_offers)
                    s=op_offers[0]
                    s_f=op_offers[0].facility_id
                if ip_offers:
                    if not n_stu.is_take_ip and ip_offers:
                        hardship_facility_id = n_stu.get_nearest_facility(ip_offers.mapped('facility_id'))
                        offer_id = hardship_facility_id.offer_ids.mapped('archive_offer_ids').filtered(lambda archive_offer_id: archive_offer_id.is_linked == False)[0]
                        s = offer_id
                        s_f=offer_id.facility_id
                type_tce1 = self.env['archive'].sudo().search([('student_id', '=', n_stu.id), ('facility_id', '=', s_f.id), ('state', 'in', ['approved', 'completed']), ('placement_type', '=', 'tce1')])
                criteria = f"""
                        <ul>
                            <li><strong>Experience Type:</strong> {self.placement_type}</li>
                            <li><strong>Placement Status:</strong> Pending</li>
                            <li><strong>Term:</strong>{self.placement_term} {self.year}</li>
                            <li><strong>Setting Type:</strong> {str(self.code)}</li>
                            <li><strong>Site Name:</strong> {str(s_f.name)}</li>
                            <li><strong>CI Contact Information:</strong> {str(s_f.address)}</li>
                        </ul>
                """
                self.env["archive"].create({
                            'student_id': n_stu.id,
                            'facility_id': s_f.id,
                            'placement_type': 'ice' if self.placement_type == 'ice' else 'tce2' if type_tce1 else 'tce1',
                            'setting': self.code,
                            'placement_term': self.placement_term,
                            'year': self.year,
                            'archive_offer_id': s.id,
                            'criteria': criteria,
                            'request_id': self.id,
                        })
                s.is_linked = True
        if len(self.archive_ids) > 0 :
            self.write({
                'state': 'done',
            })
        
        
    def filter_offers(self, student_ids, facility_ids,):...

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

    def action_complete(self):
        for rec in self.tree_ids:
            self.env["archive"].create({
                'student_id': rec.student_id.id,
                'facility_id': rec.facility_id.id,
                'geographical_id': False,
                'placement_type': self.placement_type,
                'code': self.code,
                'placement_term': self.placement_term,
                'year': self.year
            })
        self.write({
            'state': 'done',
        })
    
    def run_automatching_process(self):
        ...
    
    def action_processing_by_bot(self):
        self.write({
            'is_bot': True,
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