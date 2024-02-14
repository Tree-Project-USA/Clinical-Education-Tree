# -*- encoding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers import portal

class CustomerPortals(portal.CustomerPortal):

    @http.route(["/my/report", 
                 "/my/report/<int:placement_id>",
                 '/my/report/<model("facility.department"):department>'
                 ], 
                type="http", website=True, auth="user")
    def my_report(self, placement_id=None, department=None, report_type=None, download=False, **post):
        res_partner_id = request.env.user.partner_id
        value = {
            'res_partner_id': res_partner_id,
        }
        print(value)
        print(report_type, 'report_type')
        try:
            partner_sudo = self._document_check_access('res.partner', res_partner_id.id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=partner_sudo, report_type=report_type, report_ref='website_base.ptce3_report_actions', download=download)
        
        if post and request.httprequest.method == "POST":
            student_signature = post.get('student_signature')
            print(post)
            request.env['plcement.management'].create({
            'student_id': res_partner_id.id,
            # 'campus': post.get('campus'),
            # 'home_address': post.get('home_address'),
            'name_clinical_education_site': post.get('name_clinical_education_site'),
            'city': post.get('city'),
            'state': post.get('state'),
            # 'clinical_experience_number': post.get('clinical_experience_number'),
            # 'clinical_experience_dates': post.get('clinical_experience_dates'),
            'student_signature':  post.get('student_signature'),
            })
            # res_partner_id.write({
            #     'student_signature' : student_signature
            # })
            
    #         request.env['ir.attachment'].create({
    #         'name': 'Student Signature',
    #         'type': 'binary',
    #         'datas': post.get('student_signature'),
    #         'store_fname': 'Student Signature',
    #         'res_model': res_partner_id._name,
    #         'res_id': res_partner_id.id,
    #         'public': True
    #    })
        if department:
            print(department)
            print()
            
            scce_ids =  department.mapped("scce_ids.scce_id").ids
            print(scce_ids,'<<<<<<<<<<<')
            ci_ids = request.env["res.partner"].sudo().search([('scce_id', 'in', scce_ids)])
            value.update({
                'ci_ids': ci_ids,
                'department': department
            })
        #     department.scce_ids.ids.filtered(
        #     lambda line: line.scce_id.id == time_product.product_tmpl_id.id
        # )
            print(ci_ids)
            return request.render("website_base.ptse_general_information",value)
    
    @http.route(
        ["/show/info/ci"], type="json", auth="user", methods=['POST'], website=True, csrf=False
    )
    def show_info_ci(self, **post):
        res_partner_id = request.env.user.partner_id
        print(res_partner_id)
        ci_id = post.get('ci_id')
        rec_ci = request.env["res.partner"].sudo().search([('id', '=', int(ci_id))])
        print('========================================')
        print('========================================')
        print('========================================')
        print(post)
        value = {
            'entry_level_pt_degree_earned': rec_ci.entry_level_pt_degree_earned or '',
            'highest_degree_earned': rec_ci.highest_degree_earned or '',
            'degree_area': rec_ci.degree_area or '',
            'years_experience_ci': rec_ci.years_experience_ci or '',
            'years_experience_clinician': rec_ci.years_experience_clinician or '',
            'areas_expertise': rec_ci.areas_expertise or '',
            'clinical_certification': rec_ci.clinical_certification or '',
            'specify_area': rec_ci.specify_area or '',
            'apta_credentialed_ci': rec_ci.apta_credentialed_ci or '',
            'other_ci_credential': rec_ci.other_ci_credential or '',
            'professional_organization_membership': rec_ci.professional_organization_membership or '',
        }
        return value
  