# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Program(models.Model):
    _name = 'program'
    _description = 'Student Program'
    _rec_name = 'name'
    
    name = fields.Char(string='Name')
    num_terms = fields.Integer(string='Number of terms', default=1)
    active = fields.Boolean(string='Active')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    
    ice_term = fields.Integer(string='ICE term Number')
    tce1_term = fields.Integer(string='TCE1 term Number')
    tce2_term = fields.Integer(string='TCE2 term Number')
    program_experience_term_ids = fields.One2many(comodel_name='program.experience.term', inverse_name='program_id', string='Program Clinical Experience Terms', store=True)
    
    def action_open_program_experience_term(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.program_action')
        action['context'] = {'create': False, 'delete': False, 'default_program_id': self.id}
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.program_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.program_view_form').id, 'form')],
            'res_id': self.id,
            'target': 'new'
        })
        return action
    
    def create_update_program_experience_term(self):
        self.ensure_one()
        records = []
        experience_ids = self.env['clinical.experience'].search([('company_id', '=', self.company_id.id)])
        for experience_id in experience_ids:
            if experience_id.id not in self.program_experience_term_ids.mapped('experience_id').ids:
                records += [(0,0, {
                    'program_id': self.id,
                    'company_id': self.company_id.id,
                    'experience_id': experience_id.id,
                    'term': 0
                })]
        self.write(
            {'program_experience_term_ids': records}
        )
        
    @api.model
    def create(self, values):
        # Add code here
        res = super(Program, self).create(values)
        res.create_update_program_experience_term()
        return res
    
    
    # @api.constrains('num_terms', 'ice_term', 'tce1_term', 'tce2_term')
    # def _check_num_terms(self):
    #     for rec in self:
    #         if rec.ice_term > rec.num_terms or rec.tce1_term > rec.num_terms or rec.tce2_term > rec.num_terms:
    #             raise ValidationError("Number of terms must be greater than any other field.")
            

class ProgramExperienceTerm(models.Model):
    _name = 'program.experience.term'
    _description = 'Program Clinical Experience Term'
    _rec_name = 'program_id'
    _order = "sequence"
    
    program_id = fields.Many2one(comodel_name='program', string='Program')
    company_id = fields.Many2one('res.company', related='program_id.company_id')
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience', domain="[('company_id', '=', company_id)]")
    sequence = fields.Integer(related='experience_id.sequence', store=True)
    term = fields.Integer(string='term Number', default=1)
    start_date = fields.Date(string='start Date')
    end_date = fields.Date(string='End Date')
