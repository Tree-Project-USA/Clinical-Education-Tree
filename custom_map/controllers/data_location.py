# custom_map_controller.py
from odoo import http
import json

class CustomMap(http.Controller):

    @http.route('/location/data/', type='json')
    def get_map_data(self):

        Model = http.request.env['medical.facility']
        records = Model.sudo().search([])
        data = []

        for record in records:
            data.append({
                'clinical_site_name': record.name,
                'scce_first_name': record.scce_first_name,
                'scce_last_name': record.scce_last_name,
                'scce_email_address': record.email,
                'clinical_site_address': record.address,
                'city': record.city,
                'state': record.state,
                'name': record.geographical_id.zip_code,
                'coords': [record.geographical_id.latitude, record.geographical_id.longitude],
                'settings': [
                    {
                        'name': i.name,
                    }
                    for i in record.setting_ids
                ],
            })
        return data
