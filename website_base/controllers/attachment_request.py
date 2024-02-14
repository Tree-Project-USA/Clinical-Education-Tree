from odoo import http
from odoo.http import request

import base64
import werkzeug

class CustomerPortals(http.Controller):

    @http.route('/download_attachment', type='http', auth="public")
    def download_attachment(self, **kwargs):
        attachment_id = int(kwargs.get('id', 0))
        attachment = request.env['res.config.settings'].sudo().browse(attachment_id)

        if attachment.hardship_form_attachment:
            filecontent = base64.b64decode(attachment.hardship_form_attachment)
            headers = [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', werkzeug.urls.url_quote(attachment.name))
            ]
            return request.make_response(filecontent, headers)
        else:
            return request.not_found()
        
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
                attachment_request_id = request.env["attachment.request"].sudo().create(
                    {
                        "student_id": partner_id.id,
                        "note":  kw.get("note") if kw.get("note") else False,
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
                for attachments in range(0, int(kw.get("len_scce_attachment"))):
                    line_attachment= (0,0,{
                        'attachment_type': kw.get("scce_attachment_type_id_" + str(attachments)),
                        'expiration_date': kw.get("scce_expiration_date_" + str(attachments)),
                        'attachment_ids': [(0,0,{
                            "name": kw.get("scce_datas_" + str(attachments)).filename,
                            "datas": base64.b64encode(kw.get("scce_datas_" + str(attachments), False).read()),  
                        })],
                    })
                    attachment_list.append(line_attachment)

                attachment_request_id.sudo().write({
                    "medical_attachment_ids": attachment_list,
                })
                return request.redirect("/success/attachment/request")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
    
    @http.route("/update/hardship/request", type="http", website=True, auth="user", Methods=["POST"])
    def update_hardship_request(self, hardship=None, **post):
        partner_id = request.env.user.partner_id
        hardship_id = request.env["hardship.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ('state', '=', 'update_required')
            ], limit=1, order="id desc")
        if post and request.httprequest.method == "POST":
            try:
                zip_code_list = []
                file_list = []
                for zip in range(0, int(post.get("len_zip_code"))):
                    zip_code = request.env["geographical"].sudo().search([("zip_code", "=", post.get("zip_code_" + str(zip)))])
                    zip_code_list.append(zip_code.id)
                
                for files in range(0, int(post.get("len_file"))):
                    line_file= (0,0,{
                        'name': post.get("datas_" + str(files)).filename,
                        'datas': base64.b64encode(post.get("datas_" + str(files), False).read()),
                        'res_model': 'hardship.request',
                        'res_id': hardship_id.id,
                    })
                    file_list.append(line_file)
                hardship_id.sudo().write({
                    "note":  post.get("note") if post.get("note") else False,                    
                    "state": "under_review",
                    "attachment_ids": file_list,
                    "geographical_ids": [(6, 0, zip_code_list)],
                })
                template = request.env.ref('clinical_decision_making.mail_template_send_update_hardship_information_missing')
                template.sudo().send_mail(hardship_id.id, force_send=True)
                return request.redirect("/success/hardship/request")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
        if hardship_id:
            return request.render("website_base.update_hardship_request_template",{'hardship_id': hardship_id})
        else:
            return request.redirect("/my/home")
    
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
        # print(partner_id.name)
        # print(partner_id.mapped("archive_ids").search([]).mapped("facility_id").search([]).mapped("scce_ids").search([]))
        attachment_type_ids = request.env["scce.attachment.type"].sudo().search([])
        attachments = [{
                    'id': attachment.id,
                    'name': attachment.name
                } for attachment in attachment_type_ids]
        values["attachment_type_ids"] = attachments
        return values
