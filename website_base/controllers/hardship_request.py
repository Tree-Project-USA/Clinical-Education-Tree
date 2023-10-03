import base64
import json
from odoo import http
from odoo.http import request


class CustomerPortals(http.Controller):


    @http.route("/hardship/request", type="http", website=True, auth="public")
    def hardship_request(self):
        return request.render("website_base.hardship_request_template")

    @http.route("/create/hardship/request", type="http", website=True, auth="public", Methods=["POST"])
    def create_hardship_request(self, **kw):
        partner_id = request.env.user.partner_id
        file_list = []
        for files in range(0, int(kw.get("len_file"))):
            line= (0,0,{
                'name': kw.get("datas_" + str(files)).filename,
                'datas': base64.b64encode(kw.get("datas_" + str(files), False).read()),
            })
            file_list.append(line)
        request.env["hardship.request"].sudo().create(
            {
                "student_id": partner_id.id,
                "note":  kw.get("note") if kw.get("note") else False,
                "attachment_ids": file_list,
                "state": "draft",
            }
        )
        partner_id.sudo().write({
            "can_apply_hardship": False,
        })
        return request.redirect("/success/hardship/request")
    
    @http.route("/success/hardship/request", type="http", website=True, auth="public")
    def success_hardship_request(self):
        return request.render("website_base.success_request_template")
    
    @http.route("/info/hardship/request", type="http", website=True, auth="public")
    def info_hardship_request(self):
        values = {}
        values["partner"] = request.env.user.partner_id
        return request.render("website_base.locations_students_info_template", values)