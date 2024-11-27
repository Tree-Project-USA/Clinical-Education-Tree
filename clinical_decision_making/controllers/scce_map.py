from odoo import http
import json

class ScceMap(http.Controller):

    @http.route('/scce/map/data/', type='json', auth='user')
    def get_scce_map_data(self):

        Model = http.request.env['medical.facility']
        records = Model.search([])
        data = []

        for record in records:
            contract_histories = http.request.env['facility.contract.history'].sudo().search([('facility_id', '=', record.id)])
            facility_department = http.request.env['facility.department'].sudo().search([('facility_id', '=', record.id)])
            print(facility_department)
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
                # contract histories
                'contract_histories': [
                    {
                        'date_start': rec.date_start,
                        'date_end': rec.date_end,
                        'state': rec.state,   
                    }
                    for rec in contract_histories
                ],
                # departments
                # 'departments': [
                #     {
                #         'date_start': rec.date_start,
                #         'date_end': rec.date_end,
                #         'state': rec.state,   
                #     }
                #     for rec in facility_department
                # ],
            })
        return data
