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
    ],
    # always loaded
    "data": [

        # Views
        "views/my_account_templates.xml",
        "views/profle_template.xml",
        "views/locations_students_templates.xml",
        "views/index.xml",
        "views/hardship_request_remplates.xml",
        "views/success_hardship_request_templates.xml",
        "views/locations_students_info_templates.xml",

    ],
    # only loaded in demonstration mode
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "website_base/static/src/css/profile_user.css",
            "website_base/static/src/js/location_student.js",
            "website_base/static/src/js/file.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
    
}
