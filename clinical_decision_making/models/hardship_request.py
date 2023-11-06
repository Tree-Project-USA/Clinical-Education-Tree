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
            ('confirm', 'Validate'),
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
    
    
    def action_confirm(self):
        self.write({
            'state': 'confirm',
        })
        self.student_id.write({
            'deny_show_student': True,
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
        
    def action_update(self):
        for rec in self:
            rec.write({
                'state': 'update',
            })
            mail = (
                        self.env["mail.mail"]
                        .sudo()
                        .create(
                            {
                                "subject": _("Test Student Update HardShip"),
                                "email_from": self.env.company.email,
                                "body_html": "Dear :- {},<br/>Your hardship request needed to update. <br/><br/>Thank you,<br/>".format(
                                    rec.student_id.name
                                ),
                                "email_to": rec.student_id.email,
                            }
                        )
                        )
            mail.send()
            rec.student_id.can_apply_hardship = True
    
    # Cron job
    def check_end_date_of_hardship(self):
        hardship_ids = self.sudo().search([("state","=","confirm"), ('expiration_date', '!=', False), ("expiration_date" , "<", date.today())])
        for hardship_id in hardship_ids:
            hardship_id.action_update()
