from odoo import fields, models


class WebsiteMenu(models.Model):
    _inherit = "website.menu"


    def check_menu_hardship(self):
        return self.clean_url() != '/hardship/request' or  self.env.user.partner_id.can_apply_hardship != True and (self.env.user != self.env.ref("base.public_user"))
    def check_menu_update_hardship(self):
        hardship_id = self.env["hardship.request"].sudo().search([
            ('student_id', '=', self.env.user.partner_id.id),
            ('state', '=', 'update')
            ])
        if self.clean_url() != '/update/hardship/request' or  hardship_id:
            return True 
        else:
            return   False