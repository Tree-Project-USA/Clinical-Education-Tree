# -*- coding: utf-8 -*-
import requests
import json
from odoo.exceptions import ValidationError
from odoo import api, models, fields, _


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
    
    
class CategorySetting(models.Model):
    _name = 'category.setting'
    _description = 'Category Setting'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True)
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
                        raise ValidationError(_('The Distance Between Locations (%s) and (%s) is too small that the distance required to (%s)'% (rec.zip , location_id.zip, max_distance_mel)))
    
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
    


