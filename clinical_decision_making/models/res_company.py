from odoo import models, fields


class ResCompany(models.Model):
    
    _inherit = 'res.company'
    
    #----------------------------------------------------------
    # Fields
    #----------------------------------------------------------
    
    hardship_form_attachment = fields.Binary(
        string='Apps Menu Background Image',
        attachment=True
    )
