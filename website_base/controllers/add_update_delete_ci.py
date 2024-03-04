from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

class CiInformation(http.Controller):
    @http.route('/add/new/ci', website=True, type='http', csrf=False, auth="user", Methods=["POST"])
    def add_new_ci(self, **kw):
        partner_id = request.env.user.partner_id
        print(partner_id)
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
            ci.sudo().write({
                "partner_d": ci.id
            })
            return request.redirect("/my")
        except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
            
    @http.route('/delete/ci/<int:id>', website=True, type='http', csrf=False, auth="user", Methods=["POST"])
    def del_new_ci(self, id=None, **kw):
        partner_id = request.env["res.partner"].sudo().search([("id", "=", id)])
        try:
            partner_id.unlink()
            return request.redirect("/my")
        except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
            
    
    @http.route("/update/ci/information", website=True, type='http', csrf=False, auth="user")
    def update_ci_information(self, **post):
        partner_id = request.env["res.partner"].sudo().browse(int(post.get("scce_ids")))
        try:
            if partner_id:
                partner_data = {
                    "first_name": post.get("first_name") or False,
                    "last_name": post.get("last_name") or False,
                    "phone": post.get("phone") or False,
                    "email": post.get("email") or False,
                    "entry_level_pt_degree_earned": post.get("entry_level_pt_degree_earned") or False,
                    "highest_degree_earned": post.get("highest_degree_earned") or False,
                    "degree_area": post.get("degree_area") or False,
                    "years_experience_ci": post.get("years_experience_ci") or False,
                    "years_experience_clinician": post.get("years_experience_clinician") or False,
                    "areas_expertise": post.get("areas_expertise") or False,
                    "clinical_certification": post.get("clinical_certification") or False,
                    "specify_area": post.get("specify_area") or False,
                    "apta_credentialed_ci": post.get("apta_credentialed_ci") or False,
                    "other_ci_credential": post.get("other_ci_credential") or False,
                    "professional_organization_membership": post.get("professional_organization_membership") or False,
                }
                partner_id.sudo().write(partner_data)
            
            return request.redirect("/my")
        except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
                