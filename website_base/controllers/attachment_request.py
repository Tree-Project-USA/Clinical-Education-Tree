from odoo import http
from odoo.http import request

import base64
import werkzeug

class AttachmentRequest(http.Controller):
        
    @http.route("/attachment/request", type="http", website=True, auth="user")
    def attachment_request(self):
        values = {}
        partner_id = request.env.user.partner_id
        company_id = request.env['res.company'].sudo().search([])
        values["company_id"] =  company_id
        return request.render("website_base.attachment_request_template", values)
    
    @http.route("/create/attachment/request", type="http", website=True, auth="user", Methods=["POST"])
    def create_attachment_request(self, **kw):
        partner_id = request.env.user.partner_id
        attachment_request_id = request.env["attachment.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ])
        if kw and request.httprequest.method == "POST":
            try:
                attachment_list = []
                scce_attachment_list = []
                attachment_request_id = request.env["attachment.request"].sudo().create(
                    {
                        "student_id": partner_id.id,
                    }
                )
                scce_attachment_request_id = request.env["scce.attachment.request"].sudo().create(
                    {
                        "student_id": partner_id.id,
                    }
                )
                for attachments in range(0, int(kw.get("len_attachment"))):
                    line_attachment= (0,0,{
                        'attachment_type': kw.get("attachment_type_id_" + str(attachments)),
                        'expiration_date': kw.get("expiration_date_" + str(attachments)),
                        'attachment_ids': [(0,0,{
                            "name": kw.get("datas_" + str(attachments)).filename,
                            "datas": base64.b64encode(kw.get("datas_" + str(attachments), False).read()),  
                        })],
                    })
                    attachment_list.append(line_attachment)
                attachment_request_id.sudo().write({
                    "medical_attachment_ids": attachment_list,
                })
                for attachments in range(0, int(kw.get("len_scce_attachment"))):
                    scce_line_attachment= (0,0,{
                        'scce_attachment_type': kw.get("scce_attachment_type_id_" + str(attachments)),
                        'expiration_date': kw.get("scce_expiration_date_" + str(attachments)),
                        'attachment_ids': [(0,0,{
                            "name": kw.get("scce_datas_" + str(attachments)).filename,
                            "datas": base64.b64encode(kw.get("scce_datas_" + str(attachments), False).read()),  
                        })],
                    })
                    scce_attachment_list.append(scce_line_attachment)
                scce_attachment_request_id.sudo().write({
                    "scce_medical_attachment_ids": scce_attachment_list,
                })
                return request.redirect("/success/attachment/request")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
    
    @http.route("/success/attachment/request", type="http", website=True, auth="user")
    def success_hardship_request(self):
        return request.render("website_base.success_attachment_request_template")
    
    @http.route('/attachment', website=True, type='json', auth="user", csrf=False)
    def attachments(self, **kw):
        values = {}
        attachment_type_ids = request.env["attachment.type"].sudo().search([])
        attachments = [{
                    'id': attachment.id,
                    'name': attachment.name
                } for attachment in attachment_type_ids]
        values["attachment_type_ids"] = attachments
        return values
    
    @http.route('/scce/attachment', website=True, type='json', auth="user", csrf=False)
    def scce_attachments(self, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        archive_ids = request.env['archive'].sudo().search([
                ('student_id', '=', partner_id.id), 
            ])
        scce_list = []
        for scce_id in archive_ids.mapped("department_id").search([]).mapped("scce_ids").search([]).mapped("scce_id"):
            scce_list.append(scce_id.id)
        attachment_type_ids = request.env["scce.attachment.type"].sudo().search([("scce_id", "in", scce_list)])
        attachments = [{
                    'id': attachment.id,
                    'name': attachment.name
                } for attachment in attachment_type_ids]
        values["attachment_type_ids"] = attachments
        return values
