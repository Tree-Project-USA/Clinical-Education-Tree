# -*- encoding: utf-8 -*-
import base64
import json
from dateutil import parser

from odoo import http, _, Command
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers import portal
from odoo.addons.survey.controllers import main

class CustomerPortals(portal.CustomerPortal):

    def action_get_attachment(self,res):
        
        res_partner_id = request.env.user.partner_id
        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('website_base.ptce3_report_actions', [res.id])[0]
        b64_pdf = base64.b64encode(pdf)
        # save pdf as attachment
        name = '%s Student %s' % (dict(res._fields['stage_type'].selection).get(res.stage_type), res.student_id.name)
        return request.env['ir.attachment'].sudo().create({
            'name': name,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': name,
            'res_model': res.student_id._name,
            'res_id': res.student_id.id,
            'mimetype': 'application/pdf',
            'public': True
        })
        
    def check_data(self, data):
        return data if data else False

        
    def _get_value_plcement_management(self, value):
        campus = value.get('campus')
        home_address = value.get('home_address')
        name_clinical_education_site = value.get('name_clinical_education_site')
        city = value.get('city')
        state = value.get('state')
        clinical_experience_number =  value.get('clinical_experience_number')
        clinical_experience_dates = value.get('clinical_experience_dates' )
        student_signature = value.get('student_signature')
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
        student_signature_date = value.get('student_signature_date')
        professional_organization_membership = value.get('professional_organization_membership')
        return {
            'student_id': request.env.user.partner_id.id,
            'campus': self.check_data(campus),
            'home_address': self.check_data(home_address),
            'name_clinical_education_site': self.check_data(name_clinical_education_site),
            'city': self.check_data(city),
            'state': self.check_data(state),
            'clinical_experience_number': self.check_data(clinical_experience_number),
            'clinical_experience_dates': parser.parse(clinical_experience_dates).date(),
            'student_signature': self.check_data(student_signature) ,
            'student_signature_date': parser.parse(student_signature_date).date() ,
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
  
    @http.route(['/student/details/<int:plcement>',
                 ], 
                type="http", website=True, auth="user",Methods=["POST"])
    def _student_details(self, plcement=None, **post):
        res_partner_id = request.env.user.partner_id
        post_plcement = request.env["post.plcement.management"].sudo().search([('id', '=', plcement)])
        value = {
            'res_partner_id': res_partner_id,
            'post_plcement': post_plcement,
            'ci_ids': post_plcement.facility_id.ci_ids or '',
        }
        print('post_plcement.facility_id',post_plcement.facility_id)
        print('post_plcement.facility_id',post_plcement.facility_id.ci_ids)
        if post and request.httprequest.method == "POST":
            print(post.get('new_name'))
            new_ci = json.loads(post.get('new_name').lower()) if post.get('new_name') else False
            scce_id = post_plcement.facility_id.scce_primary_id
            print( post_plcement.facility_id.scce_primary_id,'<<<<<<<32')
            if new_ci:
              rec_ci_id = request.env['res.partner'].sudo().create({
                'is_ci': True,
                'first_name': post.get('first_name'),
                'last_name': post.get('last_name'),
                'email': post.get('email'),
                'scce_ids': [Command.link(scce_id.id)] if scce_id else False,
              })
            else:
                rec_ci_id = request.env["res.partner"].sudo().search([('id', '=', post.get('ci_id'))])
            
            post_plcement.facility_id.write({
                'ci_ids': [Command.link(rec_ci_id.id)]
            })
            value_plcement = self._get_value_plcement_management(post)
            ci_ptse = request.env['ci.ptse'].sudo().create(value_plcement)
            ci_ptse.write({'ci_id': rec_ci_id.id })
            pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('website_base.ptce3_report_actions', [ci_ptse.id])[0]
            b64_pdf = base64.b64encode(pdf)
            post_plcement.write({'ptse_3_id': ci_ptse.id })
            ci_ptse.write({'ptse_3': b64_pdf})
            self.action_get_attachment(ci_ptse)
            return request.redirect('/my')
            
        return request.render("website_base.ptse3_student_details",value)
    
    
    @http.route(['/ci/details/<int:plcement>'], 
                type="http", website=True, auth="user",Methods=["POST"])
    def ptse3_ci_details(self, ci_id=None, plcement=None, report_type=None, download=False, **post):
        plcement = request.env["ci.ptse"].sudo().search([('id', '=', plcement)])
      
        if report_type:
            try:
                plcement_sudo = self._document_check_access('ci.ptse', plcement.id)
            except (AccessError, MissingError):
                return request.redirect('/my')

            if report_type in ('html', 'pdf', 'text'):
                return self._show_report(model=plcement_sudo, report_type=report_type, report_ref='website_base.ptce3_report_actions', download=download)
        if post and request.httprequest.method == "POST":
            print(post,'post')
            print('///////////////////////////////')
            print('///////////////////////////////')
            # rec_ci_id = request.env["res.partner"].sudo().search([('id', '=', post.get('ci_id'))])
            plcement.ci_id.sudo().write({
            'first_name': post.get('first_name'),
            'last_name': post.get('last_name'),
            'email': post.get('email'),
            'entry_level_pt_degree_earned': post.get('entry_level_pt_degree_earned'),
            'highest_degree_earned': post.get('highest_degree_earned'),
            'degree_area': post.get('degree_area'),
            'years_experience_ci': post.get('years_experience_ci'),
            'years_experience_clinician': post.get('years_experience_clinician'),
            'areas_expertise': post.get('areas_expertise'),
            'clinical_certification': post.get('clinical_certification'),
            'specify_area': post.get('specify_area'),
            'apta_credentialed_ci': post.get('apta_credentialed_ci'),
            'other_ci_credential': post.get('other_ci_credential'),
            'professional_organization_membership': post.get('professional_organization_membership'),
            })
            plcement.write({
                'ci_signature': self.check_data(post.get('ci_signature')),
                'ci_signature_date':parser.parse(post.get('ci_signature_date')).date(),
                'stage_type': 'ptse3'
            })
            self.action_get_attachment(plcement)
            # plcement.ci_id.sudo().write({'ci_details_status': 'completed'})
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
        
        
    @http.route(
        ["/show/info/ci"], type="json", auth="user", methods=['POST'], website=True, csrf=False
    )
    def show_info_ci(self, **post):
        ci_id = post.get('ci_id')
        rec_ci = request.env["res.partner"].sudo().search([('id', '=', int(ci_id))])
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
    

class CustomerSurvey(main.Survey):
    
    @http.route()
    def survey_start(self, survey_token, answer_token=None, email=False, plcement=None, **post):
        result =  super(CustomerSurvey, self).survey_start(survey_token, answer_token=answer_token, email=email, **post)
        request.session['post_plcement'] = plcement
        return result
        
    def _prepare_survey_finished_values(self, survey, answer, token=False):
        result =  super(CustomerSurvey, self)._prepare_survey_finished_values(survey, answer, token=token)
        survey_id = result.get('survey')
        user_input = result.get('answer')
        post_plcement = request.env["post.plcement.management"].sudo().search([('id', '=', request.session.get('post_plcement'))])
        if survey_id.ptse_type == 'ptse_1':
           post_plcement.sudo().write({"ptse_1": user_input.id})
        else:
            post_plcement.sudo().write({"ptse_2": user_input.id})
        return result
    
    @http.route()
    def survey_display_page(self, survey_token, answer_token, **post):
        result =  super(CustomerSurvey, self).survey_display_page(survey_token, answer_token, **post)
        return result
    @http.route(['/download/answer/<int:user_input>'], 
                type="http", website=True, auth="user",Methods=["GET"])
    def _download_answer_report(self, user_input, download=True):
        user_input = request.env["survey.user_input"].sudo().search([('id', '=', user_input)])
        report = request.env["ir.actions.report"].sudo()._render_qweb_pdf('survey.certification_report', [user_input.id], data={'report_type': 'pdf'})[0]

        report_content_disposition = content_disposition('Certification.pdf')
        if not download:
            content_split = report_content_disposition.split(';')
            content_split[0] = 'inline'
            report_content_disposition = ';'.join(content_split)

        return request.make_response(report, headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(report)),
            ('Content-Disposition', report_content_disposition),
        ])

       