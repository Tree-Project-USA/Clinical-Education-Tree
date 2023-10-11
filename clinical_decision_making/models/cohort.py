# -*- coding: utf-8 -*-

import requests
from lxml.etree import LxmlError
from datetime import date
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class Cohort(models.Model):
    _name = 'cohort'
    _description = 'Cohort'
    _rec_name = 'cpdm_tree_id'

    cpdm_tree_id = fields.Many2one(comodel_name='cpdm.tree', string='cpdm Tree')
    parent_state = fields.Selection(related='cpdm_tree_id.state')
        
    # Student Information
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', domain=[('is_student', '=', True)])
    first_name = fields.Char(related='student_id.first_name')
    last_name = fields.Char(related='student_id.last_name')
    cohort_label = fields.Char(related='student_id.cohort_label')
    stu_email = fields.Char(related='student_id.email')
    stu_phone = fields.Char(related='student_id.phone')
    home_address = fields.Char(related='student_id.home_address')
    
    def get_default_avalible_student_ids(self):
        cpdm_tree_id = self.env['cpdm.tree'].browse(self.env.context.get('default_cpdm_tree_id'))
        avalible_student_ids = self.env['res.partner'].sudo().search([('is_student', '=', True), ('cohort_label', '=', cpdm_tree_id.cohort_labels), ('id', 'not in', cpdm_tree_id.cohort_ids.mapped('student_id').ids)])
        return avalible_student_ids
    
    avalible_student_ids = fields.Many2many(comodel_name='res.partner', string='Avalible Student', domain=[('is_student', '=', True)], default=get_default_avalible_student_ids, readonly=True)    
    _sql_constraints = [
        ("student_id_unique", "UNIQUE(student_id, cpdm_tree_id)", "Student is already exists"),
    ]
    stu_setting_one_id = fields.Many2one(comodel_name='category.setting', string="Setting One")
    stu_setting_two_id = fields.Many2one(comodel_name='category.setting', string="Setting Two")
    stu_setting_three_id = fields.Many2one(comodel_name='category.setting', string="Setting Three")
    
    
    # Student Locations
        # One
    stu_locatio_zip_one = fields.Char(string='Zip Code One', compute='compute_student_locations')
    stu_locatio_city_one_id = fields.Char(string='City One', compute='compute_student_locations')
    stu_locatio_state_one_id =fields.Char(string='State One', compute='compute_student_locations')
        
        # Two
    stu_locatio_zip_two = fields.Char(string='Zip Code Two', compute='compute_student_locations')
    stu_locatio_city_two_id = fields.Char(string='City Two', compute='compute_student_locations')
    stu_locatio_state_two_id =fields.Char(string='State Two', compute='compute_student_locations')
        
        # THREE
    stu_locatio_zip_three = fields.Char(string='Zip Code Three', compute='compute_student_locations')
    stu_locatio_city_three_id = fields.Char(string='City Three', compute='compute_student_locations')
    stu_locatio_state_three_id =fields.Char(string='State Three', compute='compute_student_locations')
        
        # FOUR
    stu_locatio_zip_four = fields.Char(string='Zip Code Four', compute='compute_student_locations')
    stu_locatio_city_four_id = fields.Char(string='City Four', compute='compute_student_locations')
    stu_locatio_state_four_id =fields.Char(string='State Four', compute='compute_student_locations')
        
        # FIVE
    stu_locatio_zip_five = fields.Char(string='Zip Code Five', compute='compute_student_locations')
    stu_locatio_city_five_id = fields.Char(string='City Five', compute='compute_student_locations')
    stu_locatio_state_five_id =fields.Char(string='State Five', compute='compute_student_locations')
    
        
    @api.depends('student_id.locatio_ids')
    def _compute_intershi_ice(self):
        for rec in self:
            archive_id = rec.student_id.archive_ids.filtered(lambda setting_id : setting_id.intership_period == 'ice')
            rec.stu_setting_one_id = archive_id.setting_id
            
    @api.depends('student_id.locatio_ids')
    def _compute_intershi_tce1(self):
        for rec in self:
            archive_id = rec.student_id.archive_ids.filtered(lambda setting_id : setting_id.intership_period == 'tce1')
            rec.stu_setting_two_id = archive_id.setting_id
            
    @api.depends('student_id.locatio_ids')
    def _compute_intershi_tce2(self):
        for rec in self:
            archive_id = rec.student_id.archive_ids.filtered(lambda setting_id : setting_id.intership_period == 'tce2')
            rec.stu_setting_three_id = archive_id.setting_id
            
    @api.depends('student_id', 'student_id.locatio_ids')
    def compute_student_locations(self):
        for rec in self:
            
            lines = len(rec.student_id.locatio_ids)
            
            rec.stu_locatio_zip_one = rec.student_id.locatio_ids[0].zip if lines  >= 1 else False
            rec.stu_locatio_city_one_id = rec.student_id.locatio_ids[0].city if lines  >= 1 else False
            rec.stu_locatio_state_one_id = rec.student_id.locatio_ids[0].state if lines  >= 1 else False
            
            rec.stu_locatio_zip_two = rec.student_id.locatio_ids[1].zip if lines  >= 2 else False
            rec.stu_locatio_city_two_id = rec.student_id.locatio_ids[1].city if lines  >= 2 else False
            rec.stu_locatio_state_two_id = rec.student_id.locatio_ids[1].state if lines  >= 2 else False
            
            rec.stu_locatio_zip_three = rec.student_id.locatio_ids[2].zip if lines  >= 3 else False
            rec.stu_locatio_city_three_id = rec.student_id.locatio_ids[2].city if lines  >= 3 else False
            rec.stu_locatio_state_three_id = rec.student_id.locatio_ids[2].state if lines  >= 3 else False
            
            rec.stu_locatio_zip_four = rec.student_id.locatio_ids[3].zip if lines  >= 4 else False
            rec.stu_locatio_city_four_id = rec.student_id.locatio_ids[3].city if lines  >= 4 else False
            rec.stu_locatio_state_four_id = rec.student_id.locatio_ids[3].state if lines  >= 4 else False
            
            rec.stu_locatio_zip_five = rec.student_id.locatio_ids[4].zip if lines  >= 5 else False
            rec.stu_locatio_city_five_id = rec.student_id.locatio_ids[4].city if lines  >= 5 else False
            rec.stu_locatio_state_five_id = rec.student_id.locatio_ids[4].state if lines  >= 5 else False
                   
    #-----------------------------------
    hardship_status = fields.Selection([
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved'),
    ], string='Hardship Status', compute='_compute_hardship_status', store=True, precompute=True)
    
    
    @api.depends('student_id', 'student_id.hardship_ids')
    def _compute_hardship_status(self):
        for rec in self:
            if self.parent_state == 'running':
                hardship_id = rec.student_id.hardship_ids
                if hardship_id:
                    rec.hardship_status = 'approved' if hardship_id[0].state == 'confirm' else 'not_approved'
                else:
                    rec.hardship_status = False
            else:
                if not rec.hardship_status:
                    rec.hardship_status = False
    
    # Met Rquirements
    cat_one_requirment = fields.Selection([('not_met', 'Not Met'), ('met', 'Met'),], string='CAT 1 Requirment', compute='_compute_cat_one_requirment')
    met_via = fields.Selection([('not_met', 'Not Met'), ('met_via_ice', 'Met via ICE'), ('met_via_tce_1', 'Met via TCE I'), ('met_via_tce_2', 'Met via TCE II')], string='Via CE', compute='_compute_cat_one_requirment')
    pta_supervision = fields.Selection([('not_met', 'Not Met'), ('met', 'Met'),], string='PTA Supervision')
    ipe = fields.Selection([('not_met', 'Not Met'), ('met', 'Met'),], string='IPE')
   
        
    @api.depends('stu_setting_one_id', 'stu_setting_two_id', 'stu_setting_three_id', 'ice_setting_id', 'tce1_setting_id', 'tce2_setting_id')
    def _compute_cat_one_requirment(self):
        for rec in self:
            if rec.stu_setting_one_id in [rec.ice_setting_id, rec.tce1_setting_id, rec.tce2_setting_id] or \
                rec.stu_setting_two_id in [rec.ice_setting_id, rec.tce1_setting_id, rec.tce2_setting_id] or \
                rec.stu_setting_three_id in [rec.ice_setting_id, rec.tce1_setting_id, rec.tce2_setting_id]:
                rec.cat_one_requirment = 'met'
            else:
                rec.cat_one_requirment = 'not_met'

            if rec.ice_setting_id and rec.ice_setting_id in [rec.stu_setting_one_id, rec.stu_setting_two_id, rec.stu_setting_three_id]:
                rec.met_via = 'met_via_ice'
            elif rec.tce1_setting_id and rec.tce1_setting_id in [rec.stu_setting_one_id, rec.stu_setting_two_id, rec.stu_setting_three_id]:
                rec.met_via = 'met_via_tce_1'
            elif rec.tce2_setting_id and rec.tce2_setting_id in [rec.stu_setting_one_id, rec.stu_setting_two_id, rec.stu_setting_three_id]:
                rec.met_via = 'met_via_tce_2'
            else:
                rec.met_via = 'not_met'
                

    # Placement ICE
        # Site Setting
    ice_setting_id =  fields.Many2one(comodel_name='category.setting', string="Setting")
    ice_site_id = fields.Many2one(comodel_name='site', string='ICE Site Name')
    ice_site_address = fields.Char(related='ice_site_id.address')
    ice_city = fields.Char(related='ice_site_id.city')
    ice_state = fields.Char(related='ice_site_id.state')
    ice_zip = fields.Char(related='ice_site_id.zip')
    
        # SCCE
    ice_scce_id = fields.Many2one('scce', string='ICE SCCE')
    ice_scce_first_name = fields.Char(related='ice_scce_id.first_name')
    ice_scce_last_name = fields.Char(related='ice_scce_id.last_name')
    ice_scce_email = fields.Char(related='ice_scce_id.email')

        # Accepter
    ice_placement_status = fields.Selection([('not_met', 'Confirmed'), ('met', 'Met'),], string='ICE Placement Status')
    ice_accepted_distances = fields.Boolean(string='ICE Accepted Distances', default=False)
    
    # ------------------------------------------------------------------------------
    
    # Placement TCE 1
        # Site Setting
    tce1_setting_id =  fields.Many2one(comodel_name='category.setting', string="TCE I Setting")
    tce1_site_id = fields.Many2one(comodel_name='site', string='TCE I Site Name')
    tce1_site_address = fields.Char(related='ice_site_id.address')
    tce1_city = fields.Char(related='ice_site_id.city')
    tce1_state = fields.Char(related='ice_site_id.state')
    tce1_zip = fields.Char(related='ice_site_id.zip')
    
        # SCCE
    tce1_scce_id = fields.Many2one('scce', string='TCE I SCCE')
    tce1_scce_first_name = fields.Char(related='ice_scce_id.first_name')
    tce1_scce_last_name = fields.Char(related='ice_scce_id.last_name')
    tce1_scce_email = fields.Char(related='ice_scce_id.email')

        # Accepter
    tce1_placement_status = fields.Selection([('not_met', 'Confirmed'), ('met', 'Met'),], string='TCE I Placement Status')
    tce1_accepted_distances = fields.Boolean(string='TCE II Accepted Distances', default=False)
    
    # ------------------------------------------------------------------------------
    
    # Placement TCE 2
        # Site Setting
    tce2_setting_id =  fields.Many2one(comodel_name='category.setting', string="TCE II Setting")
    tce2_site_id = fields.Many2one(comodel_name='site', string='TCE II Site Name')
    tce2_site_address = fields.Char(related='ice_site_id.address')
    tce2_city = fields.Char(related='ice_site_id.city')
    tce2_state = fields.Char(related='ice_site_id.state')
    tce2_zip = fields.Char(related='ice_site_id.zip')
    
        # SCCE
    tce2_scce_id = fields.Many2one('scce', string='TCE II SCCE')
    tce2_scce_first_name = fields.Char(related='ice_scce_id.first_name')
    tce2_scce_last_name = fields.Char(related='ice_scce_id.last_name')
    tce2_scce_email = fields.Char(related='ice_scce_id.email')

        # Accepter
    tce2_placement_status = fields.Selection([('not_met', 'Confirmed'), ('met', 'Met'),], string='TCE II Placement Status')
    tce2_accepted_distances = fields.Boolean(string='TCE II Accepted Distances', default=False)
    

    @api.depends('stu_locatio_zip_two', 'stu_locatio_zip_three', 'stu_locatio_zip_four', 'stu_locatio_zip_five', 'ice_setting_id', 'tce1_setting_id', 'tce2_setting_id')
    def get_price_total(self):
        clinical_distance_mel = self.env['ir.config_parameter'].sudo(
        ).get_param('zip_code_token')
        for rec in self:
            rec.ice_accepted_distances = False
            rec.tce1_accepted_distances = False
            rec.tce2_accepted_distances = False
            r = [rec.stu_locatio_zip_one,
            rec.stu_locatio_zip_two,
            rec.stu_locatio_zip_three,
            rec.stu_locatio_zip_four,
            rec.stu_locatio_zip_five]
            for zip in r:
                if zip:
                    distance = self.get_distance(rec.ice_setting_id, zip)
                    if distance <= clinical_distance_mel:
                        rec.ice_accepted_distances = True
                        break
            for zip in r:
                if zip:
                    distance = self.get_distance(rec.tce1_setting_id, zip)
                    if distance <= clinical_distance_mel:
                        rec.tce1_accepted_distances = True
                        break
            for zip in r:
                if zip:
                    distance = self.get_distance(rec.tce2_setting_id, zip)
                    if distance <= clinical_distance_mel:
                        rec.tce2_accepted_distances = True
                        break
                    

        self.price_total = self.quantity * self.price
    
    
    
    def action_send_email_to_students(self):
        for rec in self:
            if rec.student_id.email:
                mail = (
                            self.env["mail.mail"]
                            .sudo()
                            .create(
                                {
                                    "subject": _("Test Student Upadte Information"),
                                    "email_from": self.env.company.email,
                                    "body_html": "Dear :- {},<br/>Update Your Information <br/><br/>Thank you,<br/>".format(
                                        rec.student_id.name
                                    ),
                                    "email_to": rec.student_id.email,
                                }
                            )
                            )
                mail.send()
    
class CPDMTree(models.Model):
    _name = 'cpdm.tree'
    _description = 'Cohort'
    _rec_name = 'name'
    
    def get_cohort_label(self):
        cohort_labels = self.env['res.partner'].sudo().search([('is_student', '=', True)]).mapped('cohort_label')
        selection = [(item, item) for item in list(set(cohort_labels))]
        return selection

    name = fields.Char(string='Name')
    
    # placement_ids = fields.Many2one(comodel_name='placement.setting', string='Placement')
    cpdm_date = fields.Date('cpdm Date',default=fields.Date.today())
    
    date_begin = fields.Datetime('Start Date', required=True)
    date_end = fields.Datetime('End Date', required=True)
        
    cohort_ids = fields.One2many(comodel_name='cohort', inverse_name='cpdm_tree_id', string='Cpdm Tree')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
    ], string='state',default='draft')
    total_students  = fields.Integer(compute='_compute_total_students', string='Total Students')
    total_confirmed  = fields.Integer(compute='_compute_total_students', string='Confirmed')
    total_pending  = fields.Integer(compute='_compute_total_students', string='Pending')
    total_not_placed  = fields.Integer(compute='_compute_total_students', string='Not Placed')
    total_hardships   = fields.Integer(compute='_compute_total_students', string='Total Hardships')
    comment = fields.Html(string='Notes')
    info_ids = fields.One2many('clinic.info.gathering', 'tree_id', string='Clinic Information Gathering')
    cohort_labels = fields.Selection(selection=get_cohort_label, string='Cohort Labels', required=True)
    is_bot = fields.Boolean(string='')
    Ice = fields.Boolean(string='ICE', default=True)
    Tci1 = fields.Boolean(string='TCI 1')
    Tci2 = fields.Boolean(string='TCI 2')
    
    # avalible_student_ids = fields.Many2many(comodel_name='res.partner', string='Avalible Student', domain=[('is_student', '=', True)], compute='_compute_avalible_student_id', store=True,)
    # @api.onchange('cohort_ids.student_id', 'cohort_ids')
    # def get_avalible_student_ids(self):
    #     for rec in self:
    #         s= self.env['res.partner'].sudo().search([('is_student', '=', True), ('cohort_label', '=', rec.cohort_labels), ('id', 'not in', rec.cohort_ids.mapped('student_id').ids)])
    #         rec.write({
    #             'avalible_student_ids': s.ids
    #             }) 
                 
    @api.onchange('Tci2')
    def _onchange_Tci2(self):
        for rec in self:
            if rec.Tci2 :rec.Tci1 = True

    @api.onchange('Tci1')
    def _onchange_Tci1(self):
        for rec in self:
            if not rec.Tci1: rec.Tci2 = False

    @api.depends('cohort_ids')
    def _compute_avalible_student_id(self):
        for rec in self:
            data  = self.env['res.partner'].sudo().search([('is_student', '=', True), ('cohort_label', '=', rec.cohort_labels), ('id', 'not in', rec.cohort_ids.mapped('student_id').ids)])
            rec.avalible_student_ids = data
    
    def open_hardship_button(self):
        tree_view_id = self.env.ref('clinical_decision_making.cohort_view_tree').id
        return {
            "type": "ir.actions.act_window",
            "name": _("Placement"),
            "res_model": "cohort",
            "domain": [['cpdm_tree_id', '=', self.id]],
            "views": [[tree_view_id, "tree"], [False, "form"]],
            "context": {'default_cpdm_tree_id': self.id}
        }
    @api.depends('cohort_ids')
    def _compute_total_students(self):
        for rec in self:
            rec.total_students = len(rec.cohort_ids.mapped('student_id'))
            rec.total_confirmed = 0
            rec.total_pending = 0
            rec.total_not_placed = 0
            rec.total_hardships = 0
            
    def action_post(self):
        for rec in self :
            if not rec.info_ids :
                raise ValidationError("You Shoul Add Clinic Info")
            if any(record.state == 'not_confirmed' for record in rec.info_ids):
                raise ValidationError("You Shoul Confirm all clinic Info or deleted")
            elif any(record.num_students == 0 for record in rec.info_ids):
                raise ValidationError("Student number of all Clinck Shoul Be Bigger Than Zero")

            rec.write({
                'state': 'running',
            })
    def action_draft(self):
        self.write({
            'state': 'draft',
        })
    def action_complete(self):
        self.write({
            'state': 'done',
        })
    
    def action_processing_by_bot(self):
        self.write({
            'is_bot': True,
        })
    
    
        
    # Cron job
    def check_end_date_to_update_status(self):
        cpdm_tree_ids = self.sudo().search([("state","=","running"),("date_end" ,"<",date.today())])
        cpdm_tree_ids.sudo().write({
            "state" : "done"
            })
    
    


class ClinicInfoGathering(models.Model):
    _name = 'clinic.info.gathering'
    _description = 'Clinic information Gathering'
    
    clinc_id = fields.Many2one('site', string='Clinc(site)')
    num_students = fields.Integer(string='Number of students')
    tree_id = fields.Many2one('cpdm.tree', string='Tree')
    state = fields.Selection(
        selection=[
            ('not_confirmed', 'Not Confirmed'),
            ('confirmed', 'Confirmed'),
            ],
        string='State', default='not_confirmed')
    is_confirmed_send = fields.Boolean(string='is Confirmation Send')
    setting_type = fields.Selection([
        ('ip', 'IP'),
        ('op', 'OP'),
    ], string='Setting Type',default='ip')
    date_end = fields.Datetime('End Date')
    contract_state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Contract State', group_expand='_expand_states', copy=False,
       tracking=True, help='Status of the contract', default='draft')

    @api.onchange('clinc_id')
    def _get_state(self):
        for rec in self:
            if rec.clinc_id:
                rec.contract_state = rec.clinc_id.contract_id.state or False
                rec.date_end = rec.clinc_id.contract_id.date_end or False

    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirmed'
            })
            
    
    def action_send_email_to_clinck(self):
        for rec in self:
            if rec.clinc_id.email:
                mail = (
                            self.env["mail.mail"]
                            .sudo()
                            .create(
                                {
                                    "subject": _("Test Request confirm Hardship"),
                                    "email_from": self.env.company.email,
                                    "body_html": "Dear :- {},<br/>Test to Click confirm  <br/><br/>Thank you,<br/>".format(
                                        rec.clinc_id.name
                                    ),
                                    "email_to": rec.clinc_id.email,
                                }
                            )
                            )
                mail.send()
                rec.is_confirmed_send = True