# -*- coding: utf-8 -*-

from werkzeug.urls import url_encode
import werkzeug
from odoo.http import request
import requests
import json
from collections import defaultdict
from odoo.exceptions import ValidationError
from odoo import api, models, fields, _


class Archive(models.Model):
    _name = 'archive'
    _description = 'Archive Placement'
    _rec_name = 'student_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', readonly=True)
    site_id = fields.Many2one(comodel_name='site', string='Site', readonly=True)
    tree_id = fields.Many2one(comodel_name='cpdm.tree', string='Clinc Placement Tree', readonly=True)
    cohort_id = fields.Many2one(comodel_name='cohort', string='Cohort', readonly=True)
    date = fields.Date(string='Date',default=fields.Date.today(), readonly=True)
    
class SiteContractHistory(models.Model):
    _name = 'site.contract.history'
    _description = 'Contract history'
    _order = 'is_under_contract'
    
    contract_id = fields.Many2one('site.contract', readonly=True)

    site_id = fields.Many2one('site', string='Site', readonly=True)
    display_name = fields.Char(compute='_compute_display_name')
    name = fields.Char('Contract Name', readonly=True)
    date_start = fields.Date('Start Date', readonly=True)
    date_end = fields.Date('End Date', readonly=True)
    is_under_contract = fields.Boolean('Is Currently Under Contract', readonly=True)
    responsible_id = fields.Many2one('res.users', string='Site Responsible', readonly=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    company_country_id = fields.Many2one('res.country', string="Company country", related='company_id.country_id', readonly=True)
    country_code = fields.Char(related='company_country_id.code', depends=['company_country_id'], readonly=True)
    contract_ids = fields.One2many('site.contract', string='Contracts', compute='_compute_contract_ids', readonly=True, compute_sudo=True)
    contract_count = fields.Integer(compute='_compute_contract_count', string="# Contracts")
    under_contract_state = fields.Selection([
        ('done', 'Under Contract'),
        ('blocked', 'Not Under Contract')
    ], string='Contractual Status', compute='_compute_under_contract_state')
    activity_state = fields.Selection(related='contract_id.activity_state')

    @api.depends('is_under_contract')
    def _compute_under_contract_state(self):
        for history in self:
            history.under_contract_state = 'done' if history.is_under_contract else 'blocked'

    @api.depends('site_id.contract_ids')
    def _compute_contract_ids(self):
        sorted_contracts = self.mapped('site_id.contract_ids').sorted('date_start', reverse=True)

        mapped_site_contracts = defaultdict(lambda: self.env['site.contract'])
        for contract in sorted_contracts:
            mapped_site_contracts[contract.site_id] |= contract

        for history in self:
            history.contract_ids = mapped_site_contracts[history.site_id]

    @api.depends('site_id.name')
    def _compute_display_name(self):
        for history in self:
            history.display_name = _("%s's Contracts History", history.site_id.name)
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for history in self:
            history.contract_count = len(history.contract_ids)
            
    def site_contract_view_form_new_action(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_site_contract')
        action.update({
            'context': {'default_site_id': self.site_id.id},
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.site_contract_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.site_contract_view_form').id, 'form')],
        })
        return action
    

class SiteContracts(models.Model):
    _name = 'site.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Site Contract'
    _rec_name = 'site_id'
    
    name = fields.Char('Contract Reference', required=True)
    contract_attachment = fields.Binary(string='Contract Attachment', attachment=True)
    site_id = fields.Many2one(comodel_name='site', string='Site')
    date_start = fields.Datetime('Start Date', required=True)
    date_end = fields.Datetime('End Date', required=True)
    notes = fields.Html('Notes')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
       tracking=True, help='Status of the contract', default='draft')
    
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]
    
    def action_open_contract_form(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_site_contract')
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.site_contract_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.site_contract_view_form').id, 'form')],
            'res_id': self.id,
        })
        return action


    def _assign_open_contract(self):
        for contract in self:
            contract.site_id.sudo().write({'contract_id': contract.id})
    @api.model_create_multi
    def create(self, vals_list):
        contracts = super(SiteContracts, self).create(vals_list)
        contracts.filtered(lambda c: c.state == 'open')._assign_open_contract()
        return contracts
         
    def write(self, vals):
        old_state = {c.id: c.state for c in self}
        res = super(SiteContracts, self).write(vals)
        new_state = {c.id: c.state for c in self}
        if vals.get('state') == 'open':
            self._assign_open_contract()
        today = fields.Date.today()
        for contract in self:
            if contract == contract.site_id.contract_id \
                and old_state[contract.id] == 'open' \
                and new_state[contract.id] != 'open':
                running_contract = self.env['site.contract'].search([
                    ('site_id', '=', contract.site_id.id),
                    ('state', '=', 'open'),
                ]).filtered(lambda c: c.date_start <= today and (not c.date_end or c.date_end >= today))
                if running_contract:
                    contract.site_id.contract_id = running_contract[0]
        if vals.get('state') == 'close':
            for contract in self.filtered(lambda c: not c.date_end):
                contract.date_end = max(date.today(), contract.date_start)
        date_end = vals.get('date_end')
        if self.env.context.get('close_contract', True) and date_end and fields.Date.from_string(date_end) < fields.Date.context_today(self):
            for contract in self.filtered(lambda c: c.state == 'open'):
                contract.state = 'close'

        return res

    
class SCCE(models.Model):
    _name = 'scce'
    _description = 'SCCE'
    _rec_name = 'name'
    
    name = fields.Char(compute='_compute_field_name', string='Name')
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email Address')
    
    
    @api.depends('first_name', 'last_name')
    def _compute_field_name(self):
        for rec in self:
            rec.name = rec.first_name + ', ' + rec.last_name

class Site(models.Model):
    _name = 'site'
    _description = 'Site'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True)
    setting_ids = fields.Many2many(comodel_name='category.setting', string='Category Setting')
    address = fields.Char(string='Address')
    email = fields.Char(string='Email Address')
    city_id = fields.Many2one(comodel_name='res.city', string='City', required=True)
    country_id = fields.Many2one(comodel_name='res.country', default=lambda self: self.env.company.country_id, required=True)
    state_id = fields.Many2one(comodel_name='res.country.state', string='State', domain="[('country_id', '=', country_id)]", required=True)
    zip = fields.Char(string='Zip Code', max_length=5, required=True)
    contract_ids = fields.One2many('site.contract', 'site_id', string='Site Contracts')
    contract_id = fields.Many2one(
        'site.contract', string='Current Contract',
        domain="[('company_id', '=', company_id), ('site_id', '=', id)]", help='Current contract of the Site')

    contract_attachment = fields.Binary(string="Contract Attachment", store=True, compute='_compute_contract_warning')
    contract_warning = fields.Boolean(string='Contract Warning', store=True, compute='_compute_contract_warning')
    first_contract_date = fields.Date(compute='_compute_first_contract_date', store=True)
    contracts_count = fields.Integer(compute='_compute_contracts_count', string='Contract Count')
    
        
    @api.depends('contract_id', 'contract_id.state')
    def _compute_contract_warning(self):
        for site in self:
            site.contract_warning = not site.contract_id or site.contract_id.state != 'open'
            site.contract_attachment = site.contract_id.contract_attachment
            
    @api.depends('contract_ids.state', 'contract_ids.date_start')
    def _compute_first_contract_date(self):
        for site in self:
            site.first_contract_date = site._get_first_contract_date()
            
    def _get_first_contract_date(self, no_gap=True):
        self.ensure_one()
        def remove_gap(contracts):
            if not contracts:
                return self.env['site.contract']
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
        contract_histories = self.env['site.contract.history'].sudo().search([('site_id', 'in', self.ids)])
        for site in self:
            contract_history = len(contract_histories.filtered(lambda ch: ch.site_id == site))
            site.contracts_count = contract_history
            
    def action_open_contract_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('clinical_decision_making.site_contract_history_view_form_action')
        action['site_id'] = self.id
        action['context'] = {'default_site_id':  self.id}
        return action
    
    def print_report(self):
        return {
                    'type' : 'ir.actions.act_url',
                    'url': '/contract/attachment/%s'%(self.id),
                    'target': 'new',
        }

class CategorySetting(models.Model):
    _name = 'category.setting'
    _description = 'Category Setting'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Selection(string='Code', selection=[('ip', 'IP'), ('op', 'OP')], default='op', required=True)
    color = fields.Integer('Color Index')

class LocationSetting(models.Model):
    _name = 'location.setting'
    _description = 'Location Setting'
    _rec_name = 'student_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', required=True)
    zip = fields.Char(string='Zip Code', max_length=5)
    city_id = fields.Many2one(comodel_name='res.city', string='City')
    country_id = fields.Many2one(comodel_name='res.country', related='student_id.country_id')
    state_id = fields.Many2one(comodel_name='res.country.state', string='State', domain="[('country_id', '=', country_id)]")
    
    @api.constrains('zip', 'student_id')
    def _check_product_uom_category_id(self):
        max_distance_mel = self.env['ir.config_parameter'].sudo(
        ).get_param('max_distance_mel')
        for rec in self:
            if rec.zip:
                location_ids = self.env['location.setting'].search([('student_id', '=', rec.student_id.id), ('id', '!=', rec.id)])
                for location_id in location_ids:
                    distance = self.get_distance(rec.zip, location_id.zip)
                    if distance and distance < float(max_distance_mel):
                        raise ValidationError(_('The Distance Between zip codes (%s) and (%s) is too small that the distance required to (%s) miles'% (rec.zip , location_id.zip, max_distance_mel)))
    
    def get_distance(self, zip_one, zip_two):
        token = self.env['ir.config_parameter'].sudo(
        ).get_param('zip_code_token')
        if token:
            token= 'DemoOnly00gH8wbb344Ca9wRlS2B9Btt3Nqg7g6GkvvSswAhCSX2jtqxzmK8kWuM'
            url = 'https://www.zipcodeapi.com/rest/%s/distance.json/%s/%s/mile'% (token, zip_one, zip_two)
            res = requests.get(url)
            if res.status_code == 200:
                return res.json().get('distance')
        else:
            return False
    
class Placement(models.Model):
    _name = 'placement.setting'
    _description = 'Placement Setting'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True)
    site_id = fields.Many2one(comodel_name='site', string='Site')
    # setting_ids = fields.Many2one(comodel_name='category.setting', related='site_id.setting_ids')
    scce_id = fields.Many2one(comodel_name='scce', string='SCCE')
    
class Placement(models.Model):
    _name = 'placement.setting'
    _description = 'Placement Setting'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True)
    cohort_id = fields.Many2one(comodel_name='cohort', string='Cohort')
    # setting_ids = fields.Many2one(comodel_name='category.setting', related='site_id.setting_ids')
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', domain=[('is_student', '=', True)])
    number_of_student = fields.Integer()
    


