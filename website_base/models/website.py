from odoo import fields, models


class WebsiteMenu(models.Model):
    _inherit = "website.menu"


    def check_menu_hardship(self):
        return self.clean_url() != '/hardship/request' or  self.env.user.partner_id.can_apply_hardship != True and (self.env.user != self.env.ref("base.public_user"))
