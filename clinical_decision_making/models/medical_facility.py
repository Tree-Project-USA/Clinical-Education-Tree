# -*- coding: utf-8 -*-
from datetime import date 
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

class MedicalFacility(models.Model):
    _name = 'medical.facility'
    _inherit = ['mail.thread']
    _description = 'Medical Facility (Site)'
    _rec_name = 'name'

    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string='Active', compute='_compute_active')              
    name = fields.Char(string='Medical Facility Name', required=True)
    offer_id = fields.One2many('placement.offer', 'facility_id',string='Placement Offers', domain="[('company_id', '=', company_id)]")
    address = fields.Char(string='Address')
    email = fields.Char(related='scce_primary_id.email')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Zip Code')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip = fields.Char(related='geographical_id.zip_code')
    contract_ids = fields.One2many('facility.contract', 'facility_id', string='Medical Facility Contracts')
    contract_id = fields.Many2one(
        'facility.contract', string='Current Contract',
        domain="[('company_id', '=', company_id), ('facility_id', '=', id)]", help='Current contract of the facility', tracking=True)

    contract_attachment = fields.Binary(string="Contract Attachment", store=True, compute='_compute_contract_warning', tracking=True)
    contract_warning = fields.Boolean(string='Contract Warning', store=True, compute='_compute_contract_warning')
    first_contract_date = fields.Date(compute='_compute_first_contract_date', store=True)
    contracts_count = fields.Integer(compute='_compute_contracts_count', string='Contract Count', tracking=True)
    scce_ids = fields.One2many(comodel_name='scce.facility', inverse_name='facility_id', string='SCCE Facility', tracking=True, domain="[('company_id', '=', company_id)]")
    scce_primary_id = fields.Many2one(comodel_name='res.partner', string='Primary SCCE', domain=[('is_scce', '=', True)], tracking=True)
    scce_first_name = fields.Char(related='scce_primary_id.first_name')
    scce_last_name = fields.Char(related='scce_primary_id.last_name')
    offer_ids = fields.One2many(comodel_name='placement.offer', inverse_name='facility_id', string='Offers')
    archive_offer_count = fields.Integer(compute='_compute_archive_offer_count', string='Archive Offer Count')
    department_count = fields.Integer(compute='_compute_department_count', string='Department Count')
    department_ids = fields.One2many(comodel_name='facility.department', inverse_name='facility_id', string='Facility Department', domain="[('company_id', '=', company_id)]")
    setting_ids = fields.Many2many(comodel_name='preferred.setting', string='Setting', compute='_compute_setting_ids')    
    main_department_id = fields.Many2one(comodel_name='facility.department', string='Main Department', domain="[('company_id', '=', company_id)]")
    is_single_facility = fields.Boolean(string='Single Facility', default=True, domain="[('company_id', '=', company_id)]")
    archive_ids = fields.One2many(comodel_name='archive', inverse_name='facility_id', string='Placement History', domain="[('company_id', '=', company_id)]")
    archive_count = fields.Integer(compute='_compute_archive_count', string='Placement History Count')
    
    
    def facility_multi_department(self):
        self.write({
            'is_single_facility': False
        })
    
    @api.depends('department_ids', 'department_ids.active')
    def _compute_active(self):
        for rec in self:
            if all(not department_id.active for department_id in rec.department_ids):
                rec.active = False
            else:
                rec.active = True
    
    @api.depends('archive_ids')
    def _compute_archive_count(self):
        for rec in self:
            rec.archive_count = len(rec.archive_ids)
    
    @api.depends('offer_ids', 'offer_ids.active')
    def _compute_archive_offer_count(self):
        for rec in self:
            rec.archive_offer_count = len(rec.offer_ids.filtered(lambda x: x.active == True).mapped('archive_offer_ids'))
    
    @api.depends('department_ids', 'department_ids.active')
    def _compute_department_count(self):
        for rec in self:
            rec.department_count = len(rec.department_ids.filtered(lambda x: x.active == True or x.active == False))
            
    @api.depends('department_ids', 'department_ids.setting_ids')
    def _compute_setting_ids(self):
        for rec in self:
            rec.setting_ids = rec.department_ids.mapped('setting_ids')
        
    @api.depends('contract_id', 'contract_id.state')
    def _compute_contract_warning(self):
        for facility in self:
            facility.contract_warning = not facility.contract_id or facility.contract_id.state != 'open'
            facility.contract_attachment = facility.contract_id.contract_attachment
            
    @api.depends('contract_ids.state', 'contract_ids.date_start')
    def _compute_first_contract_date(self):
        for facility in self:
            facility.first_contract_date = facility._get_first_contract_date()
            
    def _get_first_contract_date(self, no_gap=True):
        self.ensure_one()
        def remove_gap(contracts):
            if not contracts:
                return self.env['facility.contract']
            if len(contracts) == 1:
                return contracts
            current_contract = contracts[0]
            older_contracts = contracts[1:]
            current_date = current_contract.date_start
            for i, other_contract in enumerate(older_contracts):
                gap = (current_date - (other_contract.date_end or date(2100, 1, 1))).days
                current_date = other_contract.date_start
                if gap >= 4:
                    return older_contracts[0:i] + current_contract
            return older_contracts + current_contract

        contracts = self._get_first_contracts().sorted('date_start', reverse=True)
        if no_gap:
            contracts = remove_gap(contracts)
        return min(contracts.mapped('date_start')) if contracts else False
    
    def _get_first_contracts(self):
        self.ensure_one()
        contracts = self.sudo().contract_ids.filtered(lambda c: c.state != 'cancel')
        if self.env.context.get('before_date'):
            contracts = contracts.filtered(lambda c: c.date_start <= self.env.context['before_date'])
        return contracts
    
    def _compute_contracts_count(self):
        contract_histories = self.env['facility.contract.history'].sudo().search([('facility_id', 'in', self.ids)])
        for facility in self:
            contract_history = len(contract_histories.filtered(lambda ch: ch.facility_id == facility))
            facility.contracts_count = contract_history
            
    def action_open_contract_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('clinical_decision_making.facility_contract_history_view_form_action')
        action['facility_id'] = self.id
        action['context'] = {'default_facility_id':  self.id}
        return action
    
    def print_report(self):
        return {
                    'type' : 'ir.actions.act_url',
                    'url': '/contract/attachment/%s'%(self.id),
                    'target': 'new',
        }

    # View ButtonBox Action Methods
    #------------------------------------------------------------------------------   
    def action_open_placement_offer(self):
        offer_ids = self.env['placement.offer'].search([('facility_id', '=', self.id)])
        return {
            'name': _("Facility Placement Offer"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'placement.offer',
            'domain': [('id', 'in', offer_ids.ids)],
            'context': {'default_facility_id': self.id, 'delete': False}
        }
        
    def action_open_facility_department(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_facility_department')
        action.update({
            'domain': [('id', 'in', self.department_ids.ids)],
            'context': {'default_facility_id': self.id, 'active_test': False},
        })
        return action
        
    def action_open_placement_archive_offer(self):
        archive_offer_ids = self.offer_ids.mapped('archive_offer_ids')
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_archive_offer')
        action.update({
            'view_mode': 'tree',
            'view_id': self.env.ref('clinical_decision_making.archive_offer_view_tree').id,
            'views': [(self.env.ref('clinical_decision_making.archive_offer_view_tree').id, 'tree')],
            'res_id': self.id,
            'domain': [('id', 'in', archive_offer_ids.ids), ('active', '=', True)],
        })
        return action
    
    def action_view_placement_history(self):
        self.ensure_one()
        action = self.env.ref('clinical_decision_making.archive_action').read()[0]
        action['view_mode'] = 'tree'
        action['views'] = [(self.env.ref('clinical_decision_making.archive_view_tree').id, 'tree')]
        action['view_id'] = self.env.ref('clinical_decision_making.archive_view_tree').id
        action['context'] = {'default_facility_id': self.id}
        action['domain'] = [('id', 'in', self.archive_ids.ids), ('active', '=', True)]
        return action
        
    def get_accepted_distance_students(self, student_ids):
        facility_distance_mel = self.env.company.clinical_distance_mel or 50
        students = []
        
        for student_id in student_ids:
            geographical_ids = student_id.mapped('geographical_ids')
            if geographical_ids:
                distances, dis_and_geo = self.geographical_id.get_distance_with_multi_zip_codes(geographical_ids)
                if any(distance <= facility_distance_mel for distance in distances):
                    students.append(student_id.id)
        
        return students
    
        
    # CRUD operations
    #------------------------------------------------------------------------------   
    @api.model_create_multi
    def create(self, vals_list):
        res = super(MedicalFacility, self.with_context(pass_validation=True)).create(vals_list)
        for rec in res:
            main_department_vals = {
                'name': rec.name,
                'facility_id': rec.id,
                'scce_ids': [(6, 0, rec.scce_ids.ids)],
                'setting_ids': [(6, 0, rec.setting_ids.ids)],
                'geographical_id': rec.geographical_id.id,
                'is_main_department': True
            }
            main_department_id = self.env['facility.department'].create(main_department_vals)
            rec.main_department_id = main_department_id
        return res
    
    def write(self, vals):
        res = super(MedicalFacility, self).write(vals)
        if self.main_department_id and any(field in vals for field in ['name', 'scce_ids', 'setting_ids', 'geographical_id']):
            main_department_vals = {
                'name': self.name,
                'scce_ids': [(6, 0, self.scce_ids.ids)],
                'setting_ids': [(6, 0, self.setting_ids.ids)],
                'geographical_id': self.geographical_id.id,
            }
            self.main_department_id.write(main_department_vals)
        return res

    def unlink(self):
        return super(MedicalFacility, self.with_context(unlink_main_department=True)).unlink()

    # ARCHIVES/ UNARCHIVES Methods
    #------------------------------------------------------------------------------   
    # def action_open_department_archive(self):
    #     department_ids = self.env['facility.department'].search([('id', 'in', self.facility_id.department_ids.ids)])
    #     return {
    #         'name': _("Medical Facility"),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'medical.facility',
    #         'domain': [('id', 'in', department_ids.ids)],
    #         'context': {'create': False, 'edit': False, 'delete': False},
    #         'target': 'new'
    #     }

    def action_open_department_archive(self):
        self.ensure_one() 
        if self.is_single_facility:
            if self.active:
                self.main_department_id.archive_department_and_offers()
                self.main_department_id.active = False
                self.active = False
            else:
                self.main_department_id.unarchive_department_and_offers()
                self.main_department_id.active = True
                self.active = True
        else:
            action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_active_facility_depend_wizard')
            action.update({
                'context': {'default_facility_id': self.id},
            })
            return action
class SCCEFacility(models.Model):

    _name = 'scce.facility'
    _description = 'SCCE Facility'
    _rec_name = 'scce_id'
    
    facility_id = fields.Many2one('medical.facility', string='Facility')
    scce_id = fields.Many2one('res.partner', string='SCCE', domain=[('is_scce', '=', True)])
    first_name = fields.Char(related='scce_id.first_name')
    last_name = fields.Char(related='scce_id.last_name')
    email = fields.Char(related='scce_id.email')
    phone = fields.Char(related='scce_id.phone')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    is_primary_scce = fields.Boolean(string='Is Primary SCCE', store=True,)
    is_secondary_scce = fields.Boolean(string='Is Secondary SCCE')

    
    def action_set_primary(self):
        self.ensure_one()
        scce_ids = self.facility_id.mapped('scce_ids').ids
        if scce_ids:
            self.search([('id', '!=', self.id), ('id', 'in', scce_ids)]).write({
                'is_primary_scce': False
            })
        self.facility_id.scce_primary_id = self.scce_id
        self.is_primary_scce = True
        
    def action_set_secondary(self):
        self.ensure_one()
        scce_ids = self.facility_id.mapped('scce_ids').ids
        if scce_ids:
            self.search([('id', '!=', self.id), ('id', 'in', scce_ids)]).write({
                'is_secondary_scce': False
            })
        self.is_secondary_scce = True
        
