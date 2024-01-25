from odoo import _, http
from odoo.http import request, route

class Facility(http.Controller):
    
    @http.route('/show/facility/<int:id>', website=True, type='http', auth="user")
    def show_facility(self, id=None, **kw):
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
            archive_ids = request.env['archive'].sudo().search([
                ('facility_id', '=', facility_id.id), 
            ])
            values = {
                "department_ids": facility_id.mapped("department_ids"),
                "scce_ids": facility_id.mapped("scce_ids"),
                "placement_history_ids": facility_id.mapped("archive_ids"),
                "partner_id": partner_id ,
                "facility_id": facility_id ,
                "archive_ids": archive_ids,
            }
            request.session['facility_id'] =  facility_id.id
            return request.render("website_base.show_facility_student_template", values)
  