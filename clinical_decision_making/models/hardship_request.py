# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api,_

class HardshipRequest(models.Model):
    _name = 'hardship.request'
    _inherit = ['mail.thread']
    _description = 'Hardship Request'
    _rec_name = 'student_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', domain=[('is_student', '=', True),('deny_show_student', '=', False)], tracking=True, required=True)
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
    _sql_constraints = [
        ("student_id_unique", "UNIQUE(student_id)", "You Can Not Add Hardship For student more than one"),
    ]
    expiration_date = fields.Date(string='Expiration Date')
    geographical_ids = fields.Many2many(comodel_name='geographical', string='Geographical')
    update_message = fields.Html(string='Message')
    
    
    def action_confirm(self):
        self.write({
            'state': 'confirm',
        })
        self.student_id.with_context(pass_validation=True).write({
            'deny_show_student': True,
            'geographical_ids': self.geographical_ids.ids
        })
        mail = (
                    self.env["mail.mail"]
                    .sudo()
                    .create(
                        {
                            "subject": _("Test Student Confirmation HardShip"),
                            "email_from": self.env.company.email,
                            "body_html": "Dear :- {},<br/>Your hardship request monfirmated <br/><br/>Thank you,<br/>".format(
                                self.student_id.name
                            ),
                            "email_to": self.student_id.email,
                        }
                    )
                    )
        mail.send()
        self.student_id.can_apply_hardship = False
        
    def action_cancel(self):
        self.write({
            'state': 'cancel',
        })
        self.student_id.write({
            'deny_show_student': False,
        })
        mail = (
                    self.env["mail.mail"]
                    .sudo()
                    .create(
                        {
                            "subject": _("Test Student Cancel HardShip"),
                            "email_from": self.env.company.email,
                            "body_html": "Dear :- {},<br/>Your hardship request was canceled <br/><br/>Thank you,<br/>".format(
                                self.student_id.name
                            ),
                            "email_to": self.student_id.email,
                        }
                    )
                    )
        mail.send()
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
        message = """We kindly request you to update your information as follows <br/> <div>%s</div>""" % self.update_message
        print(message)
        self.message_post(body=message,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
                partner_ids=self.student_id.ids,
                author_id=self.env.user.partner_id.id)
        message = """We kindly request you to update your information as follows <br/> <div style='color: #F8AC3D;'>%s</div>""" % self.update_message
        self.write({
            'state': 'update',
        })
        mail = (
            self.env["mail.mail"]
            .sudo()
            .create(
                {
                    "subject": _("Update Hardship Request"),
                    "email_from": self.env.company.email,
                    "body_html": self.update_message,
                    "email_to": self.student_id.email,
                }
            )
            )
        mail.send()
        self.student_id.can_apply_hardship = True
    
    # Cron job
    def check_end_date_of_hardship(self):
        hardship_ids = self.sudo().search([("state","=","confirm"), ('expiration_date', '!=', False), ("expiration_date" , "<", date.today())])
        for hardship_id in hardship_ids:
            hardship_id.action_update()
