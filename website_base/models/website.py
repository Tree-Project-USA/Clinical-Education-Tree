from odoo import fields, models


class WebsiteMenu(models.Model):
    _inherit = "website.menu"


    def check_menu_hardship(self):
        return self.clean_url() != '/hardship/request' or  not self.env["hardship.request"].sudo().search([('student_id', '=', self.env.user.partner_id.id),]) and (self.env.user != self.env.ref("base.public_user"))
            