from odoo import http
from odoo.http import request

class CustomMap(http.Controller):

    @http.route('/medical/facility/map', auth='public', website=True)
    def medical_facility_map(self, **kw):
        return request.render('custom_map.custom_map_page')
    
    