from odoo import _, http
from odoo.http import request, route

class PlacementHistory(http.Controller):
    
    @http.route("/placement/history", type="http", website=True, auth="user", Methods=["GET"])
    def placementhistory(self):
        values = {}
        res_partner_id = request.env.user.partner_id
        archive_ids = request.env['archive'].sudo().search([
                ('student_id', '=', res_partner_id.id), 
        ])
        print(archive_ids)
        values["archive_ids"] = archive_ids
        return request.render("website_base.placement_history_template", values)
    
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
                "partner_id": partner_id ,
                "facility_id": facility_id ,
                "archive_ids": archive_ids,
            }
            request.session['facility_id'] =  facility_id.id
            return request.render("website_base.show_facility_student_template", values)
  