# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api,_

class HardshipRequest(models.Model):
    _name = 'hardship.request'
    _inherit = ['mail.thread']
    _description = 'Hardship Request'
    _rec_name = 'student_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student Name', domain=[('is_student', '=', True),('deny_show_student', '=', False)], tracking=True, required=True)
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string="Attachments",
        tracking=True
    )
    note = fields.Text('Internal Notes', tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('update', 'Required Update'),
            ('under_review', 'Under Review'),
            ('confirm', 'Validate'),
            ('expired', 'Expired'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )
    expiration_date = fields.Date(string='Expiration Date')
    geographical_ids = fields.Many2many('geographical', 'geographical_ids', string='Geographical')
    student_geographical_ids = fields.Many2many('geographical', 'student_geographical_ids', string='Student Geographical')
    update_message = fields.Html(string='Message')
    attachment_cancel = fields.Binary(attachment=True)
    attachment_confirm = fields.Binary(attachment=True)
    
    def action_confirm(self):
        self.write({
            'state': 'confirm',
        })
        self.student_geographical_ids = self.student_id.geographical_ids.ids
        self.student_id.with_context(pass_validation=True).write({
            'deny_show_student': True,
            'geographical_ids': self.geographical_ids.ids
        })
        template = self.env.ref('clinical_decision_making.mail_template_send_hardship_request_approved')
        template.send_mail(self.id, force_send=True)
        self.student_id.can_apply_hardship = False

    def action_return_draft(self):
        self.write({
            'state': 'draft',
        })
        self.student_id.with_context(pass_validation=True).write({
            'deny_show_student': False,
            'geographical_ids': self.student_geographical_ids.ids
        })
        self.student_id.can_apply_hardship = True
        
    def action_attachment_file_cancel(self):
        self.attachment_cancel = False
        return {
            'name': _('Attachment File Cancel'),
            'view_mode': 'form',
            'res_model': 'hardship.request',
            'view_id': self.env.ref('clinical_decision_making.hardship_request_attachment_file_cancel_view_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }
    def action_attachment_file_confirm(self):
        self.attachment_confirm = False
        return {
            'name': _('Attachment File Confirm'),
            'view_mode': 'form',
            'res_model': 'hardship.request',
            'view_id': self.env.ref('clinical_decision_making.hardship_request_attachment_file_confirm_view_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }
    def action_cancel(self):
        self.write({
            'state': 'cancel',
        })
        self.student_id.write({
            'deny_show_student': False,
            'can_apply_hardship': False
        })
        template = self.env.ref('clinical_decision_making.mail_template_send_hardship_request_declined')
        template.send_mail(self.id, force_send=True)
        self.student_id.can_apply_hardship = True
        
    def action_open_update_view(self):
        self.update_message = False
        return {
            'name': _('Update Message'),
            'view_mode': 'form',
            'res_model': 'hardship.request',
            'view_id': self.env.ref('clinical_decision_making.hardship_request_update_view_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }
    
    
    
    def action_update(self):
        self.ensure_one()
        self.write({
            'state': 'update',
        })
        template = self.env.ref('clinical_decision_making.mail_template_send_hardship_information_missing')
        template.send_mail(self.id, force_send=True)
        self.student_id.can_apply_hardship = True
       
    
    # Cron job
    def check_end_date_of_hardship(self):
        hardship_ids = self.sudo().search([("state","=","confirm"), ('expiration_date', '!=', False), ("expiration_date" , "<", date.today())])
        for hardship_id in hardship_ids:
            hardship_id.action_update()
            
    
    @api.model
    def create(self, values):
        result = super(HardshipRequest, self).create(values)
        template = self.env.ref('clinical_decision_making.mail_template_send_hardship_request_received')
        template.send_mail(result.student_id.id, force_send=True)
        return result
    
