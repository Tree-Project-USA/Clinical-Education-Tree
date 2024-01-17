from odoo import http
from odoo.http import request

class SubmitAvailability(http.Controller):
    @http.route('/submit/availability/<int:id>', website=True, type='http', auth="user")
    def submitavailability(self, id=None, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
        company_id = request.env["res.company"].sudo().search([], limit=1)
        print(facility_id)
        # print(facility_id.name)
        SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]
        values["partner_id"] = partner_id 
        values["facility_id"] = facility_id 
        values["company_id"] = company_id 
        values["SELECTION_YEAR_RANGE"] = SELECTION_YEAR_RANGE 
        return request.render("website_base.availability_template", values)