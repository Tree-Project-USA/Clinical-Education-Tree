# -*- encoding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers import portal

class CustomerPortals(portal.CustomerPortal):

    def action_get_attachment(self,res):
        
        res_partner_id = request.env.user.partner_id
        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('website_base.ptce3_report_actions', [res.id])[0]
        b64_pdf = base64.b64encode(pdf)
        # save pdf as attachment
        name = "My Attachment"
        return request.env['ir.attachment'].sudo().create({
            'name': name,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': name,
            'res_model': res_partner_id._name,
            'res_id': res_partner_id.id,
            'mimetype': 'application/pdf',
            'public': True
        })
        
    def check_data(self, data):
        return data if data else False
        
    def _get_value_cu(self, value):
        entry_level_pt_degree_earned = value.get('entry_level_pt_degree_earned')
        highest_degree_earned = value.get('highest_degree_earned')
        degree_area = value.get('degree_area')
        years_experience_ci = value.get('years_experience_ci')
        years_experience_clinician = value.get('years_experience_clinician')
        areas_expertise = value.get('areas_expertise')
        clinical_certification = value.get('clinical_certification')
        specify_area = value.get('specify_area')
        apta_credentialed_ci = value.get('apta_credentialed_ci')
        other_ci_credential = value.get('other_ci_credential')
        professional_organization_membership = value.get('professional_organization_membership')
        
        return {
            'entry_level_pt_degree_earned': self.check_data(entry_level_pt_degree_earned),
            'highest_degree_earned': self.check_data(highest_degree_earned),
            'degree_area': self.check_data(degree_area),
            'years_experience_ci': self.check_data(years_experience_ci),
            'years_experience_clinician': self.check_data(years_experience_clinician),
            'areas_expertise': self.check_data(areas_expertise),
            'clinical_certification': self.check_data(clinical_certification),
            'specify_area': self.check_data(specify_area),
            'apta_credentialed_ci': self.check_data(apta_credentialed_ci),
            'other_ci_credential': self.check_data(other_ci_credential),
            'professional_organization_membership': self.check_data(professional_organization_membership),
        }   
        
    def _get_value_plcement_management(self, value):
        campus = value.get('campus')
        home_address = value.get('home_address')
        name_clinical_education_site = value.get('name_clinical_education_site')
        city = value.get('city')
        state = value.get('state')
        clinical_experience_number =  value.get('clinical_experience_number')
        clinical_experience_dates = value.get('clinical_experience_dates' )
        student_signature = value.get('student_signature')
        
        return {
            'student_id': request.env.user.partner_id.id,
            'campus': self.check_data(campus),
            'home_address': self.check_data(home_address),
            'name_clinical_education_site': self.check_data(name_clinical_education_site),
            'city': self.check_data(city),
            'state': self.check_data(state),
            'clinical_experience_number': self.check_data(clinical_experience_number),
            'clinical_experience_dates': self.check_data(clinical_experience_dates),
            'student_signature': self.check_data(student_signature) ,
            }
        
        
    def send_mail_ci(self, partner_id):
        group_portal = request.env.ref('base.group_portal')
        group_public = request.env.ref('base.group_public')
        user_sudo = request.env['res.users'].search([('partner_id', '=', partner_id.id), ('login', '=', partner_id.email)])
        if not user_sudo:
            
            # create a user if necessary and make sure it is in the portal group
            company = partner_id.company_id or request.env.company
            user_sudo = request.sudo().with_company(company.id)._create_user(partner_id)
            template = request.env.ref('clinical_decision_making.mail_template_send_account_creation_invitation')
            lang = user_sudo.sudo().lang
            partner = user_sudo.sudo().partner_id

            portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[partner.id]
            partner.signup_prepare()
            template.with_context(dbname=partner_id._cr.dbname, portal_url=portal_url, lang=lang).send_mail(user_sudo.id, force_send=True)

            if not user_sudo.active:
                user_sudo.write({'active': True, 'groups_id': [(4, group_portal.id), (3, group_public.id)]})
                user_sudo.partner_id.signup_prepare()
        else:
            ...
  
    @http.route(['/my/report/<model("facility.department"):department>',
                 ], 
                type="http", website=True, auth="user",Methods=["POST"])
    def ptse3_student_details(self, ci_id=None, department=None, report_type=None, download=False, **post):
        res_partner_id = request.env.user.partner_id
        value = {
            'res_partner_id': res_partner_id,
        }
        print(value)
        print(report_type, 'report_type')
        # try:
        #     partner_sudo = self._document_check_access('res.partner', res_partner_id.id)
        # except (AccessError, MissingError):
        #     return request.redirect('/my')

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=partner_sudo, report_type=report_type, report_ref='website_base.ptce3_report_actions', download=download)
        
        if post and request.httprequest.method == "POST":
            print(post)
            rec_ci_id = request.env["res.partner"].sudo().search([('id', '=', ci_id)])
            print(ci_id)
            value_ci = self._get_value_cu(post)
            rec_ci_id.write(value_ci)
            value_plcement = self._get_value_plcement_management(post)
            plcement = request.env['plcement.management'].sudo().create(value_plcement)
            plcement.write({
                'ci_id': rec_ci_id.id,
                'facility_id': department.facility_id.id,
            })
            pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('website_base.ptce3_report_actions', [plcement.id])[0]
            b64_pdf = base64.b64encode(pdf)
            plcement.write({'ptse_3': b64_pdf})
            self.action_get_attachment(plcement)
            return request.redirect('/my')

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
            # rec_ci = request.env["res.partner"].browse(ci_id)
            rec_ci = request.env["res.partner"].sudo().search([('id', '=', ci_id)])
            # ci_ids = request.env["res.partner"].sudo().search([('scce_id', 'in', scce_ids)])
            value.update({
                'ci':rec_ci,
                'department': department
            })
        #     department.scce_ids.ids.filtered(
        #     lambda line: line.scce_id.id == time_product.product_tmpl_id.id
        # )
            # print(ci_ids)
            return request.render("website_base.ptse3_student_details",value)
    
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
    
    @http.route(['/my/report/<int:plcement_id>'], 
                type="http", website=True, auth="user",Methods=["POST"])
    def ptse3_ci_details(self, ci_id=None, plcement_id=None, report_type=None, download=False, **post):
        if plcement_id:
            plcement = request.env['plcement.management'].sudo().search([('id', '=', plcement_id)])
        if post and request.httprequest.method == "POST":
            print(post)
            plcement.write({
                'ci_signature': self.check_data(post.get('ci_signature')),
                'ci_signature_date': self.check_data(post.get('ci_signature_date')),
                'stage_type': 'ptse3'
            })
        value = {
            'is_ci': request.env.user.partner_id.is_ci,
            'plcement':plcement
        }
        
        return request.render("website_base.ptse3_ci_details",value)
    
    @http.route(['/add/ci/<model("facility.department"):department>',
                 ], 
                type="http", website=True, auth="user",Methods=["POST"])
    def _add_new_ci(self, department=None, **post):
        scce =  department.facility_id.scce_ids.filtered(
            lambda line: line.is_primary_scce is True
        )
        print(department,'department')
        print('===================')
        print('===================')
        print('===================')
        print('===================')
        print('===================')
        ci = request.env['res.partner'].sudo().create({
            'scce_ids': [(6, 0, scce)],
            'facility_id':  department.facility_id.id,
            'is_ci': True, 
            'first_name': self.check_data(post.get('first_name')), 
            'last_name': self.check_data(post.get('last_name')), 
            'email': self.check_data(post.get('email')), 
            'entry_level_pt_degree_earned': self.check_data(post.get('entry_level_pt_degree_earned')), 
            'highest_degree_earned': self.check_data(post.get('highest_degree_earned')), 
            'degree_area': self.check_data(post.get('degree_area')), 
            'years_experience_ci': self.check_data(post.get('years_experience_ci')), 
            'years_experience_clinician': self.check_data(post.get('years_experience_clinician')), 
            'areas_expertise': self.check_data(post.get('areas_expertise')), 
            'clinical_certification': self.check_data(post.get('clinical_certification')), 
            'specify_area': self.check_data(post.get('specify_area')), 
            'apta_credentialed_ci': self.check_data(post.get('apta_credentialed_ci')), 
            'other_ci_credential': self.check_data(post.get('other_ci_credential')), 
            'professional_organization_membership': self.check_data(post.get('professional_organization_membership')), 
        })
        return request.redirect("/my/report/%s?ci_id=%s" % (slug(department), ci.id))
        