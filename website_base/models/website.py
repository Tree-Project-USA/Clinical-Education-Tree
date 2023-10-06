from odoo import fields, models


class WebsiteMenu(models.Model):
    _inherit = "website.menu"


    def _compute_visible(self):
        super()._compute_visible()
        for menu in self:
            partner_id = self.env.user.partner_id
            if partner_id.can_apply_hardship == True:
                if menu.clean_url() == "/hardship/request":
                    menu.is_visible = False