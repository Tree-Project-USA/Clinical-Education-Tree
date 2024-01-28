import base64
import requests
from datetime import datetime
import json
from odoo import _, http
from odoo.http import request, route, content_disposition
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortals(CustomerPortal):
    
    @route([])
    def home(self):
        values = {}
        res_partner_id = request.env.user.partner_id
        if not res_partner_id.is_scce:
            hardship_id = request.env["hardship.request"].sudo().search([
                ('student_id', '=', res_partner_id.id)
            ], limit=1, order="id desc")
            attachment_request_id = request.env["attachment.request"].sudo().search([
                ('student_id', '=', res_partner_id.id)
            ], limit=1, order="id desc")
            print(attachment_request_id)
            archive_ids = request.env['archive'].sudo().search([
                ('student_id', '=', res_partner_id.id), 
            ])
            hardship_ids = request.env["hardship.request"].sudo().search([
                ('student_id', '=', res_partner_id.id)])
            values["hardship_id"] = hardship_id
            values["hardship_ids"] = hardship_ids
            values["archive_ids"] = archive_ids
            values["partner"] = res_partner_id
            values["locations"] = res_partner_id.geographical_ids
            values["preferred_setting_ids"] = res_partner_id.preferred_setting_ids
            values["medical_attachment_ids"] = res_partner_id.medical_attachment_ids
            return request.render("website_base.user_profile_templates", values)
        else:
            scce_facility_ids = request.env["scce.facility"].sudo().search([
                ('scce_id', '=', res_partner_id.id)]).mapped("facility_id")
            values["partner"] = res_partner_id
            values["scce_facility_ids"] = scce_facility_ids
            return request.render("website_base.scce_profile_template", values)
        
    @http.route(['/download/attachment/<int:id>'], type='http', auth='public', website=True)
    def download_attachment(self, id):
        report_id = request.env['ir.attachment'].sudo().search([('id', '=', id)], limit=1)
        if report_id:
            content_base64 = base64.b64decode(report_id.datas)
            mimetype = guess_mimetype(content_base64)
            pdfhttpheaders = [
                ('Content-Type', mimetype),
                ('Content-Length', len(content_base64)),
                ('Content-Disposition', content_disposition(report_id.name)),
            ]
            return request.make_response(content_base64, headers=pdfhttpheaders)
        