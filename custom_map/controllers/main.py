from odoo import http
from odoo.http import request

class CustomMap(http.Controller):

    @http.route('/my/custom/map', auth='public', website=True)
    def custom_map(self, **kw):
        return request.render('custom_map.custom_map_page')
    
    