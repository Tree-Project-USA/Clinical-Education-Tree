# -*- encoding: utf-8 -*-
import base64
from odoo import http, _, Command
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
            'ci_details_status': 'not_started',
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
            template = request.env.ref('clinical_decision_making.mail_template_send_account_creation_invitation')
            template.sudo().send_mail(user_sudo.id, force_send=True)
  
    @http.route(['/student/details/<int:department>',
                 ], 
                type="http", website=True, auth="user",Methods=["POST"])
    def _student_details(self, ci_id=None, department=None, **post):
        res_partner_id = request.env.user.partner_id
        department = request.env["facility.department"].sudo().search([('id', '=', department)])
        value = {
            'res_partner_id': res_partner_id,
        }
        if post and request.httprequest.method == "POST":
            rec_ci_id = request.env["res.partner"].sudo().search([('id', '=', ci_id)])
            value_ci = self._get_value_cu(post)
            rec_ci_id.write(value_ci)
            value_plcement = self._get_value_plcement_management(post)
            print(value_plcement)
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

        if department and ci_id:
            rec_ci = request.env["res.partner"].sudo().search([('id', '=', ci_id)])
            plcement = request.env["plcement.management"].sudo().search([('ci_id', '=', rec_ci.id)])
            if plcement:
                error = _('CI Details Have Already Been Created')
                return request.redirect_query('/show/department/%s' % department.id, {"error": error})
            value.update({
                'ci':rec_ci,
                'department': department
            })
            
            return request.render("website_base.ptse3_student_details",value)
    
    
    @http.route(['/ci/details/<int:plcement>'], 
                type="http", website=True, auth="user",Methods=["POST"])
    def ptse3_ci_details(self, ci_id=None, plcement=None, report_type=None, download=False, **post):
        plcement = request.env["plcement.management"].sudo().search([('id', '=', plcement)])
      
        if report_type:
            try:
                plcement_sudo = self._document_check_access('plcement.management', plcement.id)
            except (AccessError, MissingError):
                return request.redirect('/my')

            if report_type in ('html', 'pdf', 'text'):
                return self._show_report(model=plcement_sudo, report_type=report_type, report_ref='website_base.ptce3_report_actions', download=download)
        if post and request.httprequest.method == "POST":
          
            plcement.write({
                'ci_signature': self.check_data(post.get('ci_signature')),
                'ci_signature_date': self.check_data(post.get('ci_signature_date')),
                'stage_type': 'ptse3'
            })
            plcement.ci_id.sudo().write({'ci_details_status': 'completed'})
        value = {
            'is_ci': request.env.user.partner_id.is_ci,
            'plcement':plcement,
            'ci_id': plcement.sudo().ci_id
        }
        
        return request.render("website_base.ptse3_ci_details",value)
    
    @http.route(['/add/ci/<int:department>',
                 ], 
                website=True, type='http', csrf=False, auth="user", Methods=["POST"])
    def _add_new_ci(self, department=None, **post):
        department = request.env["facility.department"].sudo().search([('id', '=', department)])
        scce =  department.facility_id.scce_ids.sudo().filtered(
            lambda line: line.is_primary_scce is True
        )
        print(scce, '<<<<<<<<<<<<<<<')
        ci = request.env['res.partner'].sudo().create({
            'scce_ids': [Command.link(new_scce.id) for new_scce in scce],
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
        department.facility_id.sudo().write({
                        'ci_ids': [Command.link(ci.id)]
                    })
        return request.redirect("/student/details/%s?ci_id=%s" % (department.id, ci.id))
        