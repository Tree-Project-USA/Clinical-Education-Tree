{
    "name": "Website Base",
    "summary": "Website Base",
    "description": "",
    "author": "Nomowsoft",
    "category": "Uncategorized",
    "version": "15.0.1.0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "website",
        "clinical_decision_making",
    ],
    # always loaded
    "data": [
        
        # Data
        'data/data.xml',
        'data/mail_data.xml',
        # Views
        "views/my_account_templates.xml",
        "views/profle_template.xml",
        "views/locations_students_templates.xml",
        "views/hardship_request_remplates.xml",
        "views/update_hardship_request_remplates.xml",
        "views/success_hardship_request_templates.xml",
        "views/locations_students_info_templates.xml",
        "views/error_request_template.xml",
        "views/preferred_setting_template.xml",

    ],
    # only loaded in demonstration mode
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "website_base/static/src/css/profile_user.css",
            "website_base/static/src/scss/style.scss",
            "website_base/static/src/js/location_student.js",
            "website_base/static/src/js/location_student_hard_ship.js",
            "website_base/static/src/js/location_student_update_hard_ship.js",
            "website_base/static/src/js/file.js",
            "website_base/static/src/js/website_update_information.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
    
}
