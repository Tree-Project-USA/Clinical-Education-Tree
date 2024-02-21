from odoo import http
from odoo.http import request


class UpdateScceInformation(http.Controller):
      
    @http.route("/save/changes/ci_information", type="json", auth="user", methods=['POST'], website=True, csrf=False)
    def save_changes_ci_information(self, **post):
        try:
            partner_id = request.env.user.partner_id
            partner_id.sudo().write({
                "phone": post.get("phone") if post.get("phone") else False,
                "email": post.get("email") if post.get("email") else False,
                "entry_level_pt_degree_earned": post.get("entry_level_pt_degree_earned") if post.get("entry_level_pt_degree_earned") else False,
                "highest_degree_earned": post.get("highest_degree_earned") if post.get("highest_degree_earned") else False,
                "degree_area": post.get("degree_area") if post.get("degree_area") else False,
                "years_experience_ci": post.get("years_experience_ci") if post.get("years_experience_ci") else False,
                "years_experience_clinician": post.get("years_experience_clinician") if post.get("years_experience_clinician") else False,
                "areas_expertise": post.get("areas_expertise") if post.get("areas_expertise") else False,
                "clinical_certification": post.get("clinical_certification") if post.get("clinical_certification") else False,
                "specify_area": post.get("specify_area") if post.get("specify_area") else False,
                "apta_credentialed_ci": post.get("apta_credentialed_ci") if post.get("apta_credentialed_ci") else False,
                "other_ci_credential": post.get("other_ci_credential") if post.get("other_ci_credential") else False,
                "professional_organization_membership": post.get("professional_organization_membership") if post.get("professional_organization_membership") else False,
            })
            return True
        except Exception as e:
                return False
            