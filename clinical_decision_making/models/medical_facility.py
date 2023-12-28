# -*- coding: utf-8 -*-
from datetime import date 
from odoo import models, fields, api, _

class MedicalFacility(models.Model):
    _name = 'medical.facility'
    _inherit = ['mail.thread']
    _description = 'Medical Facility (Site)'
    _rec_name = 'name'

    
    name = fields.Char(string='Medical Facility Name', required=True)
    offer_id = fields.One2many('placement.offer', 'facility_id',string='Placement Offers')
    address = fields.Char(string='Address')
    email = fields.Char(string='Email Address')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Geographical', required=True)
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
    scce_ids = fields.Many2many(comodel_name='scce', string='SCCES', tracking=True)
    offer_ids = fields.One2many(comodel_name='placement.offer', inverse_name='facility_id', string='Offers')
    archive_offer_count = fields.Float(compute='_compute_archive_offer_count', string='Archive Offer Count')
    
    @api.depends('offer_ids')
    def _compute_archive_offer_count(self):
        for rec in self:
            rec.archive_offer_count = len(rec.offer_ids.mapped('archive_offer_ids'))
        
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
    
    def action_open_placement_archive_offer(self):
        archive_offer_ids = self.offer_ids.mapped('archive_offer_ids')
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_archive_offer')
        action.update({
            'view_mode': 'tree',
            'view_id': self.env.ref('clinical_decision_making.archive_offer_view_tree').id,
            'views': [(self.env.ref('clinical_decision_making.archive_offer_view_tree').id, 'tree')],
            'res_id': self.id,
            'domin': [('id', 'in', archive_offer_ids.ids)],
        })
        return action
        
    def get_accepted_distance_students(self, student_ids):
        facility_distance_mel = float(self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel'))
        students = []
        
        for student_id in student_ids:
            geographical_ids = student_id.mapped('geographical_ids')
            if geographical_ids:
                distances, dis_and_geo = self.geographical_id.get_distance_with_multi_zip_codes(geographical_ids)
                if any(distance <= facility_distance_mel for distance in distances):
                    students.append(student_id.id)
        
        return students