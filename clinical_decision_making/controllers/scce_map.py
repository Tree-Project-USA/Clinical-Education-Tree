from odoo import http
import json

class ScceMap(http.Controller):

    @http.route('/scce/map/data/', type='json', auth='user')
    def get_scce_map_data(self):

        Model = http.request.env['medical.facility']
        records = Model.search([])
        data = []

        for record in records:
            data.append({
                'clinical_site_name': record.name,
                'scce_email_address': record.email,
                'clinical_site_address': record.address,
                'city': record.city,
                'state': record.state,
                'name': record.geographical_id.zip_code,
                'coords': [record.geographical_id.latitude, record.geographical_id.longitude]
            })
        return data
