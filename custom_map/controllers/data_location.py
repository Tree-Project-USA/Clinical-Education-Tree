# custom_map_controller.py
from odoo import http
import json

class CustomMap(http.Controller):

    @http.route('/custom_map/data/', type='json', auth='public', website=True)
    def get_map_data(self):
        # Example: Fetching data from a model
        Model = http.request.env['geographical.preferred']  # Replace 'your.model' with the actual model name
        records = Model.search([])  # Fetch all records; customize as needed
        data = []

        for record in records:
            data.append({
                'name': record.zip,
                'coords': [record.latitude, record.longitude]  # Adjust field names as needed
            })
            
        return data
