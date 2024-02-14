from odoo import _, http
from odoo.http import request, route

class Facility(http.Controller):
    
    @http.route('/show/department/<int:id>', website=True, type='http', auth="user")
    def show_department(self, id=None, **kw):
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            department_id = request.env["facility.department"].sudo().search([("id", "=", id)])

            archive_ids = request.env['archive'].sudo().search([
                ('department_id', '=', department_id.id), 
                ('student_id', '=', partner_id.id),
            ])
            values = {
                "department_id": department_id,
                "scce_ids": department_id.mapped("scce_ids"),
                "archive_ids": archive_ids,
            }
            return request.render("website_base.show_facility_student_template", values)
  