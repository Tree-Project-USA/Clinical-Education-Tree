# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Maror(models.Model):
    _name = 'maror.maror'
    _description = 'maror.maror'

    def get_default_country(self):
        country = self.env.ref("base.ye")
        return country and country.id or False
    name = fields.Char()
    birth_date = fields.Date()
    mobile = fields.Char(string='Mobile')
    phone = fields.Char(string='Phone')
    identity_type = fields.Selection([
        ('id_card', 'ID Card'),
        ('passport', 'Passport'),
        ('birth_certificate', 'Birth Certificate'),
    ], string='Identity Type')
    gender = fields.Selection([
        ("male","Male"),
        ("fmale","Fmale")
    ], string='Gender')
    image = fields.Binary(string='Image')
    blood_type = fields.Char(string='Blood Type')
    description = fields.Text()
    state_id   = fields.Many2one('res.country.state', string='State', index=True)
    country_id = fields.Many2one('res.country', default=get_default_country)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('accept', 'Accepted'),
        ('reject', 'Rejected'),
        ('rquired_update', 'Required Update')
    ], 'Status', default="draft")
    
    def action_accept(self):
        self.status = 'accept'
        
    def action_reject(self):
        self.status = 'reject'

    def action_set_to_draft(self):       
        self.status = 'draft'
    # def action_set_to_update(self):       
    #     self.status = 'required_update'
        
    @api.model
    def create(self, vals):
        # Agregar codigo de validacion aca
        self.action_set_to_draft()
        return super(Maror, self).create(vals)



