from odoo import _, http
from odoo.http import request, route

class PlacementHistory(http.Controller):
    
    @http.route("/placement/history", type="http", website=True, auth="user", Methods=["GET"])
    def placementhistory(self):
        values = {}
        res_partner_id = request.env.user.partner_id
        values["partner"] = res_partner_id
        return request.render("website_base.placement_history_template", values)
  