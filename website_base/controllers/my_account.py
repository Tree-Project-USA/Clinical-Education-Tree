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
        if not res_partner_id.is_scce and not res_partner_id.is_ci:
            scce_list = []
            archive_ids = request.env['archive'].sudo().search([
                ('student_id', '=', res_partner_id.id), 
            ])
            hardship_id = request.env["hardship.request"].sudo().search([
                ('student_id', '=', res_partner_id.id)
            ], limit=1, order="id desc")
            medical_attachment_id = request.env["attachment.request"].sudo().search([
                ('student_id', '=', res_partner_id.id)
            ])
            scce_medical_attachment_id = request.env["scce.attachment.request"].sudo().search([
                ('student_id', '=', res_partner_id.id)
            ])
            for scce_id in archive_ids.mapped("department_id").search([]).mapped("scce_ids").search([]).mapped("scce_id"):
                scce_list.append(scce_id.id)
            attachment_type_id = request.env["attachment.type"].sudo().search([])
            scce_attachment_type_id = request.env["scce.attachment.type"].with_company(res_partner_id.company_id.id).search([("scce_id", "in", scce_list)])
            hardship_ids = request.env["hardship.request"].sudo().search([
                ('student_id', '=', res_partner_id.id)])
            values["hardship_id"] = hardship_id
            values["hardship_ids"] = hardship_ids
            values["archive_ids"] = archive_ids
            values["partner"] = res_partner_id
            values["locations"] = res_partner_id.preferred_geographical_ids
            values["preferred_setting_ids"] = res_partner_id.preferred_setting_ids
            values["medical_attachment_ids"] = res_partner_id.medical_attachment_ids
            values["scce_medical_attachment_ids"] = res_partner_id.scce_medical_attachment_ids
            values["medical_attachment_id"] = medical_attachment_id
            values["scce_medical_attachment_id"] = scce_medical_attachment_id
            values["attachment_type_id"] = attachment_type_id
            values["scce_attachment_type_id"] = scce_attachment_type_id
            return request.render("website_base.user_profile_templates", values)
        elif res_partner_id.is_scce:
            scce_facility_ids = request.env["scce.facility"].sudo().search([
                ('scce_id', '=', res_partner_id.id)]).mapped("facility_id")
            placement_offer_ids = request.env["placement.offer"].sudo().search([
                ('scce_id', '=', res_partner_id.id)
            ])
            values["partner"] = res_partner_id
            scce_list = []
            for i in res_partner_id.search([("is_ci", "=", True)]).mapped("scce_ids"):
                scce_list.append(i.id)

            values["ci"] = request.env["res.partner"].sudo().search([
                ("is_ci", "=", True),
                ("scce_ids.scce_id", "in", res_partner_id.ids)
            ])
            values["placement_offer_ids"] = placement_offer_ids
            values["scce_facility_ids"] = scce_facility_ids
            return request.render("website_base.scce_profile_template", values)
        elif res_partner_id.is_ci:
            scce_facility_ids = request.env["scce.facility"].sudo().search([
                ('scce_id', 'in', res_partner_id.scce_ids.ids)]).mapped("facility_id")
            
            post_plcement_ids = request.env["post.plcement.management"].sudo().search([
                ('ci_id', '=', res_partner_id.id)])
          
            values["partner"] = res_partner_id
            values["scce_facility_ids"] = scce_facility_ids
            values["plcement_ids"] = post_plcement_ids
            return request.render("website_base.ci_profile_template", values)
        
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
        