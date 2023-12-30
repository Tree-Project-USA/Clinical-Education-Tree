from odoo import http
from odoo.http import request


class UpdateInformation(http.Controller):

    @http.route("/update/information", type="http", website=True, auth="user", Methods=["POST"])
    def update_inforamtion(self, **post):
        partner_id = request.env.user.partner_id
        if post and request.httprequest.method == "POST":
            try:
                partner_id.sudo().write({
                    "home_address":  post.get("home_address") if post.get("home_address") else False,                    
                    "mobile": post.get("mobile") if post.get("mobile") else False,
                    "phone": post.get("phone") if post.get("phone") else False,
                    "email": post.get("email") if post.get("email") else False,
                    "personal_phone": post.get("personal_phone") if post.get("personal_phone") else False,
                })
                template = request.env.ref('clinical_decision_making.mail_template_send_update_of_personal_information')
                template.send_mail(partner_id.id, force_send=True)
                    
                return request.redirect("/my")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
