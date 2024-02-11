# Copyright 2013-2017 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WebsiteMenu(models.Model):
    """Improve website.menu with adding booleans that drive
    if the menu is displayed when the user is logger or not.
    """

    _inherit = "website.menu"

    def _compute_visible(self):
        """Display the menu item whether the user is logged or not."""
        super()._compute_visible()
        for menu in self:
            if menu.clean_url() == "/contactus":
                menu.is_visible = False
