from odoo import http
from odoo.http import request


class UpdateScceInformation(http.Controller):
      
    @http.route("/save/changes/scce_information", type="json", auth="user", methods=['POST'], website=True, csrf=False)
    def save_changes_scce_information(self, **post):
         try:
                partner_id = request.env.user.partner_id
                partner_id.sudo().write({
                    "phone": post.get("phone") if post.get("phone") else False,
                    "email": post.get("email") if post.get("email") else False,
                })
                return True
         except Exception as e:
                return False