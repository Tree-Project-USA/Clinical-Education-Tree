# -*- coding: utf-8 -*-

import math
import requests
from odoo.exceptions import ValidationError
from odoo import models, fields, api
    
class Geographical(models.Model):
    _name = 'geographical'
    _description = 'Geographical Data'
    _rec_name = 'zip_code'
    
    zip_code = fields.Char(string='Zip Code', readonly=True)
    state = fields.Char(string='State', readonly=True)
    city = fields.Char(string='City', readonly=True)
    latitude = fields.Char(string='latitude', readonly=True)
    longitude = fields.Char(string='Longitude', readonly=True)
    
    _sql_constraints = [
        ('zip_code_uniq', 'unique(zip_code)', 'ther is already zip code as this !')
    ]

    @api.model
    def find_or_create_zip_code(self, zipcode):
        zip_code_id = self.search([('zip_code', '=', zipcode)])
        if not zip_code_id:
            locstion_info = self.get_locstion_informations(zipcode)
            zip_code_id = self.create({
                'zip_code': locstion_info['zip_code'],
                'state': locstion_info['state'],
                'city': locstion_info['city'],
                'latitude': locstion_info['lat'],
                'longitude': locstion_info['lng']
            })
        return zip_code_id
    
    @api.model
    def get_locstion_informations(self, zipcode):
        token = self.env.company.zip_code_token
        try:
            if token:
                url = "https://www.zipcodeapi.com/rest/%s/info.json/%s/degrees" % (token, zipcode)
                res = requests.request("GET", url)
                if res.status_code == 200:
                    return res.json()
                else:
                    raise ValidationError(res.json().get('error_msg', ''))
            else:
                raise ValidationError('Token Is invalidate')
        except Exception as e:
            raise ValidationError(str(e))
    
    def get_state_zip_codes(self):
        self.ensure_one()
        zip_codes = self.search([('state', '=', self.state)]).mapped('zip_code')
        return zip_codes

    def get_distance_with_zip_code(self, zip_code):
        # Convert latitude and longitude to radians
        lon1 = float(self.longitude)
        lat1 = float(self.latitude)
        lon2 = float(zip_code.longitude)
        lat2 = float(zip_code.latitude)
        

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 3958.8 * c  # Earth's radius in miles

        return distance, {zip_code: distance}
    
    def get_distance_with_multi_zip_codes(self, zip_codes):
        # Convert latitude and longitude to radians
        distances = []
        geographical_and_distances = {}
        for zip_code in zip_codes:
            distance, dis_and_geo  = self.get_distance_with_zip_code(zip_code)
            distances.append(distance)
            geographical_and_distances.update(dis_and_geo)
        return distances, geographical_and_distances
    
    def get_zip_codes_state(self, zip_codes):
        return zip_codes.filtered(lambda zip_code: zip_code.state == self.state)
    
    def get_all_zip_code_state(self, zip_codes):
        return list(set(zip_codes.mapped('state')))
    
    @api.model
    def create(self, vals):
        vals['zip_code'] = str(int(vals['zip_code']))
        return super(Geographical, self).create(vals)
    
class geographicalPreferred(models.Model):
    _name = 'geographical.preferred'
    _description = 'Preferred Addresses'
    _rec_name = 'student_id'
    
    def _default_sequence(self):
        return self.env.company.normal_number_zipcodes

    sequence = fields.Integer('Sequence', default=_default_sequence)
    student_id = fields.Many2one(comodel_name='res.partner', string='Student')
    hardship_id = fields.Many2one(comodel_name='hardship.request', string='Hardship Request')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Zip Code', required=True)
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip = fields.Char(related='geographical_id.zip_code')
    
class geographicalHistory(models.Model):
    _name = 'geographical.history'
    _description = 'Geographical History'
    _rec_name = 'student_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student')
    archive_id = fields.Many2one(comodel_name='archive', string='Archive')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Geographical')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip = fields.Char(related='geographical_id.zip_code')