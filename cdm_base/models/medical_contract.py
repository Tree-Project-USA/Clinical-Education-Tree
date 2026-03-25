# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from collections import defaultdict
from odoo import api, models, fields, _

    
class FacilityContractHistory(models.Model):
    _name = 'facility.contract.history'
    _description = 'Contract history'
    _order = 'is_under_contract'
    
    contract_id = fields.Many2one('facility.contract', readonly=True)
    facility_id = fields.Many2one('medical.facility', string='Clinical Site', readonly=True)
    display_name = fields.Char(compute='_compute_display_name')
    name = fields.Char('Contract Name', readonly=True)
    date_start = fields.Date('Start Date', readonly=True)
    date_end = fields.Date('End Date', readonly=True)
    is_under_contract = fields.Boolean('Is Currently Under Contract', readonly=True)
    responsible_id = fields.Many2one('res.users', string='Clinical Site Responsible', readonly=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True)
    company_id = fields.Many2one('res.company', string='University', readonly=True)
    company_country_id = fields.Many2one('res.country', string="Company country", related='company_id.country_id', readonly=True)
    country_code = fields.Char(related='company_country_id.code', depends=['company_country_id'], readonly=True)
    contract_ids = fields.One2many('facility.contract', string='Contracts', compute='_compute_contract_ids', readonly=True, compute_sudo=True)
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

    @api.depends('facility_id.contract_ids')
    def _compute_contract_ids(self):
        sorted_contracts = self.mapped('facility_id.contract_ids').sorted('date_start', reverse=True)

        mapped_facility_contracts = defaultdict(lambda: self.env['facility.contract'])
        for contract in sorted_contracts:
            mapped_facility_contracts[contract.facility_id] |= contract

        for history in self:
            history.contract_ids = mapped_facility_contracts[history.facility_id]

    @api.depends('facility_id.name')
    def _compute_display_name(self):
        for history in self:
            history.display_name = _("%s Contract History", history.facility_id.name)
    
    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for history in self:
            history.contract_count = len(history.contract_ids)
            
    def facility_contract_view_form_new_action(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('cdm_base.action_facility_contract')
        action.update({
            'context': {'default_facility_id': self.facility_id.id, 'default_name': '%s - ' % self.facility_id.name},
            'view_mode': 'form',
            'view_id': self.env.ref('cdm_base.facility_contract_view_form').id,
            'views': [(self.env.ref('cdm_base.facility_contract_view_form').id, 'form')],
        })
        return action
    

class FacilityContracts(models.Model):
    _name = 'facility.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Clinical Site Contract'
    _rec_name = 'facility_id'
    
    
    name = fields.Char('Contract Reference', required=True)
    contract_attachment = fields.Binary(string='Contract Attachment', attachment=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Clinical Site')
    company_id = fields.Many2one('res.company', related='facility_id.company_id', store=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date')
    notes = fields.Html('Notes')
    state = fields.Selection([
        ('draft', 'Contract Initiated'),
        ('open', 'Active Contract'),
        ('require_renewal', 'Require Renewal'),
        ('close', 'Expired'),
        ('cancel', 'Inactive Contract')
    ], string='Status', group_expand='_expand_states', copy=False,
       tracking=True, help='Status of the contract', default='draft')
    
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def action_open_contract_form(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('cdm_base.action_facility_contract')
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('cdm_base.facility_contract_view_form').id,
            'views': [(self.env.ref('cdm_base.facility_contract_view_form').id, 'form')],
            'res_id': self.id,
        })
        return action

    def facility_contract_view_form_renewal_action(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('cdm_base.action_facility_contract')
        action.update({
            'context': {'default_facility_id': self.facility_id.id,
                        'default_name': self.name,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref('cdm_base.facility_contract_view_form_wizard').id,
            'views': [(self.env.ref('cdm_base.facility_contract_view_form_wizard').id, 'form')],
            'target': 'new'
        })
        return action

    # Cron job
    def action_require_renewal(self):
        contract_notify_months = self.env.company.contract_notify_months
        current_date = datetime.now()
        future_date = current_date + timedelta(days=contract_notify_months*30)
        contract_ids = self.env['facility.contract'].sudo().search([("state","=","open"), ('future_date', '!=', False), ("date_end" , "<", future_date)])
        contract_ids.sudo().write({
            "state" : "require_renewal"
            })
        
    def action_expired_contract(self):
        current_date = datetime.now()
        contract_ids = self.env['facility.contract'].sudo().search([("state", "in", ["open", 'require_renewal']), ("date_end" , ">=", current_date)])
        contract_ids.sudo().write({
            "state" : "close"
            })

    def action_cancel(self):
        self.write({
            'state': 'cancel',
        })

    def _assign_open_contract(self):
        for contract in self:
            contract.facility_id.sudo().write({'contract_id': contract.id})
        
    @api.model_create_multi
    def create(self, vals_list):
        contracts = super(FacilityContracts, self).create(vals_list)
        contracts.filtered(lambda c: c.state == 'open')._assign_open_contract()
        return contracts
         
    def write(self, vals):
        old_state = {c.id: c.state for c in self}
        res = super(FacilityContracts, self).write(vals)
        new_state = {c.id: c.state for c in self}
        if vals.get('state') == 'open':
            self._assign_open_contract()
        today = fields.Date.today()
        for contract in self:
            if contract == contract.facility_id.contract_id \
                and old_state[contract.id] == 'open' \
                and new_state[contract.id] != 'open':
                running_contract = self.env['facility.contract'].search([
                    ('facility_id', '=', contract.facility_id.id),
                    ('state', '=', 'open'),
                ]).filtered(lambda c: c.date_start <= today and (not c.date_end or c.date_end >= today))
                if running_contract:
                    contract.facility_id.contract_id = running_contract[0]
        if vals.get('state') == 'close':
            for contract in self.filtered(lambda c: not c.date_end):
                contract.date_end = max(date.today(), contract.date_start)
        date_end = vals.get('date_end')
        if self.env.context.get('close_contract', True) and date_end and fields.Date.from_string(date_end) < fields.Date.context_today(self):
            for contract in self.filtered(lambda c: c.state == 'open'):
                contract.state = 'close'

        return res

