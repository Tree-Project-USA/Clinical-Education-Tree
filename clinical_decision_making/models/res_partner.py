# -*- coding: utf-8 -*-
import requests
import json
from odoo.tools import email_normalize
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_student = fields.Boolean(string='Is Student', default=False)
    studentid = fields.Char(string='Student ID', copy=False)
    name = fields.Char(string='Student Name', compute='_compute_name', store=True, default='Student Name')
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True )
    cohort_label = fields.Char(string='Cohort', compute='_compute_term_fields', store=True)# TODO: Remoove this line
    hardship_ids = fields.One2many('hardship.request', 'student_id', string='Hardship')
    home_address = fields.Char(string='Home Address')
    personal_phone = fields.Char(string='Personal Phone')
    personal_email_address = fields.Char(string='Personal Email Address')
    campus = fields.Char(string='Campus', default='Austin, TX')
    archive_ids = fields.One2many(comodel_name='archive', inverse_name='student_id', string='Placement History')
    can_apply_hardship = fields.Boolean(string='Apply Hardship', default=False)
    is_reach_maximum_zip_code = fields.Boolean(string='Reach Maximum Zip Code', default=False)
    deny_show_student = fields.Boolean()
    geographical_ids = fields.Many2many(comodel_name='geographical', string='Geographical')
    program_id = fields.Many2one(comodel_name='program', string='Program Duration', )
    program_type = fields.Char(string='Program Type', default='DPT')
    start_term_type = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Start Term', )
    start_year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Start Year', )
    start_term = fields.Char(string='Start Term', compute='_compute_term_fields', store=True)
    graduation_term = fields.Char(string='Graduation Term/Year', compute='_compute_term_fields', store=True)
    is_with_hardship = fields.Boolean(string='is_with_hardship', compute='_compute_is_with_hardship',  store=True)
    ice_term = fields.Char(string='ICE Term', compute='_compute_term_fields', store=True)
    tce1_term = fields.Char(string='TCE1 Term', compute='_compute_term_fields', store=True)
    tce2_term = fields.Char(string='TCE2 Term', compute='_compute_term_fields', store=True)
    is_take_ip = fields.Boolean(compute='_compute_is_take_ip', string='Is Take IP')
    is_complete_ice = fields.Boolean(compute='_compute_term',string='Is Complate Ice', store=True)
    is_complete_tce1 = fields.Boolean(compute='_compute_term', string='Is Complate Tec1', store=True)
    is_complete_tce2 = fields.Boolean(compute='_compute_term', string='Is Complate Tec2', store=True)   
    aval_archive_ids = fields.Many2many(comodel_name='archive', string='Archive', compute='get_aval_archive_ids', readonly=False)
    preferred_setting_ids = fields.Many2many(comodel_name='preferred.setting', string='Preferred Setting')
    hardship_count = fields.Integer(compute='_compute_hardship_count', string='HardShip Count')
    alternative_schedule_count = fields.Integer(compute='_compute_alternative_schedule_count', string='Alternative Schedule Count')
    alternative_schedule_ids = fields.One2many('alternative.schedule', 'student_id', string='Alternative Schedule')
    medical_attachment_ids = fields.One2many(comodel_name='attachments', inverse_name='student_id', string='Medical Document')
    
    @api.onchange('archive_ids', 'archive_ids.archive_offer_id')
    def _onchange_archive_ids(self):
        for rec in self:
            for res in rec.archive_ids:
                res.archive_offer_id.student_id = self.id
    
    
    @api.depends('hardship_ids')
    def _compute_hardship_count(self):
        for rec in self:
            rec.hardship_count = len(rec.hardship_ids)
            
    @api.depends('hardship_ids')
    def _compute_alternative_schedule_count(self):
        for rec in self:
            rec.alternative_schedule_count = len(rec.alternative_schedule_ids)
    
    def _create_user(self,partner_id):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': email_normalize(partner_id.email),
            'login': email_normalize(partner_id.email),
            'partner_id': partner_id.id,
            'company_id': partner_id.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })

    
    def action_send_account_creation_invitation(self):
        group_portal = self.env.ref('base.group_portal')
        group_public = self.env.ref('base.group_public')
        partner_ids = self.env['res.partner'].search([('email', '!=', False),('is_student', '=', True)])
        for partner_id in partner_ids:
                user_sudo = self.env['res.users'].search([('partner_id', '=', partner_id.id), ('login', '=', partner_id.email)])
                if not user_sudo:
                  
                    # create a user if necessary and make sure it is in the portal group
                    company = partner_id.company_id or self.env.company
                    user_sudo = self.sudo().with_company(company.id)._create_user(partner_id)
                    template = self.env.ref('clinical_decision_making.mail_template_send_account_creation_invitation')
                    lang = user_sudo.sudo().lang
                    partner = user_sudo.sudo().partner_id

                    portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[partner.id]
                    partner.signup_prepare()
                    template.with_context(dbname=partner_id._cr.dbname, portal_url=portal_url, lang=lang).send_mail(user_sudo.id, force_send=True)

                    if not user_sudo.active:
                        user_sudo.write({'active': True, 'groups_id': [(4, group_portal.id), (3, group_public.id)]})
                        user_sudo.partner_id.signup_prepare()

    @api.depends('archive_ids')
    def get_aval_archive_ids(self):
        for rec in self:
            rec.aval_archive_ids = rec.archive_ids.filtered(lambda x: x.placement_status != 'not_placed')
            
    @api.depends('archive_ids')
    def _compute_is_take_ip(self):
        for rec in self:
            rec.is_take_ip = True if rec.archive_ids.filtered(lambda x: x.setting == 'ip' and x.placement_status != 'not_placed') else False
    
    @api.depends('archive_ids')
    def _compute_term(self):
        for rec in self:
            rec.is_complete_ice = True if self.env['archive'].search([('student_id', '=', rec.id), ('placement_type', '=', 'ice'), ('placement_status', 'in', ['completed',])]) else False
            rec.is_complete_tce1 = True if self.env['archive'].search([('student_id', '=', rec.id), ('placement_type', '=', 'tce1'), ('placement_status', 'in', ['completed',])]) else False
            rec.is_complete_tce2 = True if self.env['archive'].search([('student_id', '=', rec.id), ('placement_type', '=', 'tce2'), ('placement_status', 'in', ['completed',])]) else False
        
    @api.depends('hardship_ids', 'hardship_ids.state')
    def _compute_is_with_hardship(self):
        for rec in self:
            rec.is_with_hardship = True if self.env['hardship.request'].search([('student_id', '=', rec.id), ('state', '=', 'approved')]) else False
            
    @api.depends('start_year', 'start_term_type', 'program_id', 'alternative_schedule_ids', 'alternative_schedule_ids.state', 'alternative_schedule_ids.year', 'alternative_schedule_ids.term')
    def _compute_term_fields(self):
        for rec in self:
            try:
                if rec.start_year and rec.start_term_type  and rec.program_id:
                    rec.start_term = self.convert_term_year(rec.start_term_type, rec.start_year)
                    alternative_schedule = [self.convert_term_year(x.term, x.year) for x in rec.alternative_schedule_ids.filtered(lambda x:x.state == 'confirmed')]
                    graduation_t, graduation_y = rec.calculate_end_term(rec.start_term_type, rec.start_year, rec.program_id.num_terms, alternative_schedule)
                    rec.graduation_term = self.convert_term_year(graduation_t, graduation_y)
                    
                    print('-------------------------------- Alternative Schedule: ', alternative_schedule)
                    print(self.get_specific_term_year(rec.start_term_type, rec.start_year, rec.program_id.num_terms, rec.program_id.ice_term, alternative_schedule))
                    ice_term_t, ice_term_y = self.get_specific_term_year(rec.start_term_type, rec.start_year, rec.program_id.num_terms, rec.program_id.ice_term, alternative_schedule)
                    rec.ice_term = self.convert_term_year(ice_term_t, ice_term_y)
                    
                    tce1_term_t, tce1_term_y = self.get_specific_term_year(rec.start_term_type, rec.start_year, rec.program_id.num_terms, rec.program_id.tce1_term, alternative_schedule)
                    rec.tce1_term = self.convert_term_year(tce1_term_t, tce1_term_y)
                    
                    tce2_term_t, tce2_term_y = self.get_specific_term_year(rec.start_term_type, rec.start_year, rec.program_id.num_terms, rec.program_id.tce2_term, alternative_schedule)
                    rec.tce2_term = self.convert_term_year(tce2_term_t, tce2_term_y)
                    if tce2_term_t == 'spring':
                        rec.cohort_label = f"{tce2_term_y}-04-{rec.campus}-{rec.program_type}"
                    elif tce2_term_t == 'summer':
                        rec.cohort_label = f"{tce2_term_y}-08-{rec.campus}-{rec.program_type}"
                    elif tce2_term_t == 'fall':
                        rec.cohort_label = f"{tce2_term_y}-12-{rec.campus}-{rec.program_type}"
                else:
                    rec.start_term = ''
                    rec.graduation_term = ''
                    rec.ice_term = ''
                    rec.tce1_term = ''
                    rec.tce2_term = ''
            except:
                    rec.start_term = ''
                    rec.graduation_term = ''
                    rec.ice_term = ''
                    rec.tce1_term = ''
                    rec.tce2_term = ''
                    
    def action_open_hardship(self):
        return {
            'name': _("Student Hardship"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hardship.request',
            'domain': [('id', 'in', self.hardship_ids.ids)],
            'context': {'default_student_id': self.id, 'delete': False}
        }
    
    # @api.onchange('geographical_ids')
    # def _onchange_geographical_ids(self):
    #     self.ensure_one()
    #     if not self.env.context.get('pass_validation', False) or not self.is_with_hardship:
    #         print(self.geographical_ids)
    #         for rec in self.geographical_ids:
    #             if rec.id in self.geographical_ids.filtered(lambda x : x.id != rec.id).mapped('id'):
    #                 raise ValidationError(_('Zip code must be unique. '))
    #         self.check_zip_code_distance(self.geographical_ids)
    #         self.check_validation_zip_code_state(self.geographical_ids)

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.first_name if record.first_name else ''} {record.last_name if record.last_name else ''}"
    
    def check_zip_code_distance(self, geographical_ids):
        max_distance_mel = self.env['ir.config_parameter'].sudo(
        ).get_param('max_distance_mel')
        
        for geographical_id in geographical_ids:
            zipcoe_ids, dis_and_geo = geographical_id.get_distance_with_multi_zip_codes(geographical_ids - geographical_id)
            for zip_code, distance in dis_and_geo.items():
                if distance < float(max_distance_mel):
                    raise ValidationError(_('The Distance Between zip codes (%s) and (%s) is (%s) and  too small that the distance required to (%s) miles'% (geographical_id.zip_code , zip_code.zip_code, distance, max_distance_mel)))
    
    def check_validation_zip_code_state(self, geographical_ids):
        max_zipcodes_state = self.env['ir.config_parameter'].sudo().get_param('max_zipcodes_state') or 3
        max_zipcodes_state = int(max_zipcodes_state)

        for geographical_id in geographical_ids:
            zipcoe_ids = geographical_id.get_zip_codes_state(geographical_ids)
            all_states = geographical_id.get_all_zip_code_state(geographical_ids)
            if len(zipcoe_ids) > max_zipcodes_state:
                    raise ValidationError(_('You can only add maximum (%s) zip code in same state' % max_zipcodes_state))

            if len(all_states) < 3:
                    raise ValidationError('You Should add at least 3 different state.')
    
    @api.constrains('email')
    def validate_mail(self):
        if self.email:
            if not re.match('^[_A-Za-z0-9-]+(\.[_A-Za-z0-9-]+)*@[_A-Za-z0-9-]+(\.[_A-Za-z0-9-]+)*(\.[A-Za-z]{2,4})$', self.email):
                raise ValidationError(_('The personal email address must be valid ( example@example.com )'))
            
    @api.constrains('geographical_ids')
    def _check_geographical_ids(self):
        self.ensure_one()
        if self.env.context.get('pass_validation', False) or self.is_with_hardship:
            return

        if not self.env.context.get('pass_validation', False) or not self.is_with_hardship:
            normal_number_zipcodes = self.env['ir.config_parameter'].sudo().get_param('normal_number_zipcodes') or 5
            normal_number_zipcodes = int(normal_number_zipcodes)
            print(normal_number_zipcodes)
            if len(self.geographical_ids) < normal_number_zipcodes or len(self.geographical_ids) > normal_number_zipcodes:
                    raise ValidationError(_('Count of zip codes shuld be %s' % normal_number_zipcodes))
                
            for rec in self.geographical_ids:
                if rec.id in self.geographical_ids.filtered(lambda x : x.id != rec.id).mapped('id'):
                    raise ValidationError(_('Zip code must be unique. '))
            self.check_zip_code_distance(self.geographical_ids)
            self.check_validation_zip_code_state(self.geographical_ids)

    def _check_unique_studentid(self, studentid):
        if studentid:
            pattern = r'^\d+$'
            if not re.match(pattern, studentid):
                raise ValidationError(_('The Student ID Must Contain Numbers Only'))
            students_ids = self.env['res.partner'].search_count(
                    [
                    ("studentid", "in", [studentid]),
                    ("is_student", "=", True)
                    ])
            if students_ids > 1:
                raise ValidationError(_(f'The Student ID : {studentid} Already Exists'))

    @api.model
    def _get_studentid_sequence(self):
        code = self.env['ir.sequence'].next_by_code('res_partner_sequence')
        students_ids = self.env['res.partner'].search_count(
            [
            ("studentid", "=", code),
            ("is_student", "=", True)
            ])
        if not students_ids:
            return code
        else:
            return self._get_studentid_sequence()


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['studentid'] = self._get_studentid_sequence()
        return super(ResPartner, self.with_context(pass_validation=True)).create(vals_list)

    @api.constrains('preferred_setting_ids')
    def validate_preferred_setting_ids(self):
        if self.env.context.get('pass_validation', False):
            return
        for rec in self:
            if len(rec.preferred_setting_ids) < 5:
                raise ValidationError(_('Must be selected 5 preferred settings'))
    
    def calculate_end_term(self, start_term, start_year, num_terms, alternative_schedule=[]):
        terms = ["spring", "summer", "fall"]
        start_index = terms.index(start_term)
        current_index = start_index
        current_year = int(start_year)

        # Calculate the end term
        i = 0
        while i < num_terms - 1:
            current_index += 1
            if current_index == len(terms):
                current_index = 0
                current_year += 1
            term = self.convert_term_year(terms[current_index], current_year)
            if term not in alternative_schedule:
                i += 1

        return terms[current_index], current_year
    
    def get_specific_term_year(self, start_term, start_year, num_terms, target_term_index, alternative_schedule=[]):
        terms = ["spring", "summer", "fall"]

        start_index = terms.index(start_term)
        current_index = start_index
        current_year = int(start_year)
        counter = 1
        
        i = 0
        while i < num_terms - 1:
            current_index += 1
            if current_index == len(terms):
                current_index = 0
                current_year += 1
            term = self.convert_term_year(terms[current_index], current_year)
            if term not in alternative_schedule:
                i += 1
                counter += 1
                
            if counter == target_term_index:
                return terms[current_index], current_year
    
    def convert_term_year(self, term, year):
        term_abbr = ""
        if term.lower() == "fall":
            term_abbr = "FA"
        elif term.lower() == "spring":
            term_abbr = "SP"
        elif term.lower() == "summer":
            term_abbr = "SU"

        year_abbr = str(year)[-2:]

        term_year = term_abbr + year_abbr

        return term_year

    def get_accepted_distance_facility(self, facility_ids, facility_distance_mel=50):
        print(facility_distance_mel)
        facility_distance_mel = float(facility_distance_mel) or float(self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')) or 50
        accepted_facility_ids = set()

        geographical_ids = self.mapped('geographical_ids')
        for geographical_id in geographical_ids:
            distances = geographical_id.get_distance_with_multi_zip_codes([f.geographical_id for f in facility_ids])[0]
            accepted_facility_ids.update([f.id for f, distance in zip(facility_ids, distances) if distance <= facility_distance_mel])

        return list(accepted_facility_ids)
    
    def get_nearest_facility(self, facility_ids):
        data = []
        geographical_ids = self.mapped('geographical_ids')
        for geographical_id in geographical_ids:
            for facility_id in facility_ids:
                distance, dis_and_geo = geographical_id.get_distance_with_zip_code(facility_id.geographical_id)
                data.append((facility_id, distance, geographical_id))
        return  (min(data, key=lambda x: x[1])[0], min(data, key=lambda x: x[1])[2]) if min(data, key=lambda x: x[1]) else (False, False)
    
    def get_nearby_facility_zipcode(self, facility_id):
        facility_distance_mel = float(self.env['ir.config_parameter'].sudo().get_param('clinical_distance_mel')) or 50
        geographical_ids = self.mapped('geographical_ids')        
        for geographical_id in geographical_ids:
            distance, dis_and_geo = geographical_id.self.get_distance_with_zip_code(facility_id.geographical_id)
            if distance <= facility_distance_mel:
                return geographical_id
            
    def write(self, vals):
        if any(field in vals for field in ['home_address', 'phone', 'personal_phone', 'personal_email_address']):
            template = self.env.ref('clinical_decision_making.mail_template_send_update_of_personal_information')
            template.sudo().send_mail(self.id, force_send=True)
        return super(ResPartner, self).write(vals)

    @api.onchange('preferred_setting_ids')
    def _compute_preferred_setting_ids(self):
        for rec in self:
            if rec.preferred_setting_ids:
                list_type_setting_op = []
                list_type_setting_ip = []
                if len(rec.preferred_setting_ids) > 5:
                    raise ValidationError(_('Only allowed 5 preferred settings'))
                for setting_id in rec.preferred_setting_ids:
                    if setting_id.type_setting == 'op':
                        list_type_setting_op.append(setting_id._origin.id)
                    else:
                        list_type_setting_ip.append(setting_id._origin.id)
                if len(list_type_setting_op) == 5 or len(list_type_setting_ip) == 5:
                    raise ValidationError(_('You should have one (IP) as minimum and one (OP)'))
    
    
    def alternative_schedule_term_action(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_alternative_schedule')
        action.update({
            'name': 'Alternative Schedule of %s' % self.name,
            'context': {'default_student_id': self.id},
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.alternative_schedule_form_view_wizard').id,
            'views': [(self.env.ref('clinical_decision_making.alternative_schedule_form_view_wizard').id, 'form')],
            'target': 'new'
        })
        return action
    
    # Smart Button Action Methods
    #------------------------------------------------------------------------------   
    def action_view_alternative_schedule(self):
        action = self.env.ref('clinical_decision_making.action_alternative_schedule').read()[0]
        action['domain'] = [('id', 'in', self.alternative_schedule_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        return action
    
    def archive_unarchive_student(self):
        self.ensure_one()
        if self.active:
            self.active = False
        else:
            self.active = True
        
        