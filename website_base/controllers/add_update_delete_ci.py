from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

class CiInformation(http.Controller):
    @http.route('/add/new/ci', website=True, type='http', csrf=False, auth="user", Methods=["POST"])
    def add_new_ci(self, **kw):
        partner_id = request.env.user.partner_id
        try:
            ci = request.env["res.partner"].sudo().create({
                "scce_ids": [(6,0, partner_id.ids)], 
                "is_ci": True, 
                "first_name": kw.get("first_name"),
                "last_name": kw.get("last_name"),
                "phone": kw.get("phone"),
                "email": kw.get("email"),
                "facility_id": int(kw.get("facility_id")),
                "entry_level_pt_degree_earned": kw.get("entry_level_pt_degree_earned"),
                "highest_degree_earned": kw.get("highest_degree_earned"),
                "degree_area": kw.get("degree_area"),
                "years_experience_ci": kw.get("years_experience_ci"),
                "years_experience_clinician": kw.get("years_experience_clinician"),
                "areas_expertise": kw.get("areas_expertise"),
                "clinical_certification": kw.get("clinical_certification"),
                "specify_area": kw.get("specify_area"),
                "apta_credentialed_ci": kw.get("apta_credentialed_ci"),
                "other_ci_credential": kw.get("other_ci_credential"),
                "professional_organization_membership": kw.get("professional_organization_membership"),
            })
            return request.redirect("/my")
        except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
            
    @http.route('/delete/ci/<int:id>', website=True, type='http', csrf=False, auth="user", Methods=["POST"])
    def add_new_ci(self, id=None, **kw):
        partner_id = request.env["res.partner"].sudo().search([("id", "=", id)])
        try:
            partner_id.unlink()
            return request.redirect("/my")
        except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
            