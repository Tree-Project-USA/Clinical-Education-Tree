import base64
import json
from odoo import http
from odoo.http import request


class CustomerPortals(http.Controller):


    @http.route("/hardship/request", type="http", website=True, auth="user")
    def hardship_request(self):
        return request.render("website_base.hardship_request_template")
    @http.route("/update/hardship/request", type="http", website=True, auth="user", Methods=["POST"])
    def update_hardship_request(self, hardship=None, **post):
        partner_id = request.env.user.partner_id
        hardship_id = request.env["hardship.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ('state', '=', 'update')
            ])
        if post and request.httprequest.method == "POST":
            HardshipRequest = request.env["hardship.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ('state', '=', 'update')
            ])
            file_list = []
            for files in range(0, int(post.get("len_file"))):
                line= (0,0,{
                    'name': post.get("datas_" + str(files)).filename,
                    'datas': base64.b64encode(post.get("datas_" + str(files), False).read()),
                })
            file_list.append(line)
            HardshipRequest.sudo().write({
                "note":  post.get("note") if post.get("note") else False,
                "attachment_ids": file_list,
                "state": "draft",
            })
            return request.redirect("/")
        if hardship_id:
            return request.render("website_base.update_hardship_request_template",{'hardship_id': hardship_id})
        else:
            return request.redirect("/")

    @http.route("/create/hardship/request", type="http", website=True, auth="user", Methods=["POST"])
    def create_hardship_request(self, **kw):
        partner_id = request.env.user.partner_id
        file_list = []
        for files in range(0, int(kw.get("len_file"))):
            line= (0,0,{
                'name': kw.get("datas_" + str(files)).filename,
                'datas': base64.b64encode(kw.get("datas_" + str(files), False).read()),
            })
            file_list.append(line)
        HardshipRequest = request.env["hardship.request"].sudo().create(
            {
                "student_id": partner_id.id,
                "note":  kw.get("note") if kw.get("note") else False,
                "attachment_ids": file_list,
                "state": "draft",
            }
        )
        partner_id.sudo().write({
            "can_apply_hardship": True,
        })
        template = request.env.ref('website_base.mail_template_send_hardship_request')
        template.sudo().send_mail(HardshipRequest.id, force_send=True)
        return request.redirect("/success/hardship/request")
    
    @http.route("/success/hardship/request", type="http", website=True, auth="public")
    def success_hardship_request(self):
        return request.render("website_base.success_request_template")
    
    @http.route("/info/hardship/request", type="http", website=True, auth="public")
    def info_hardship_request(self):
        values = {}
        values["partner"] = request.env.user.partner_id
        return request.render("website_base.locations_students_info_template", values)