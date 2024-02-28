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
        # Views
        "views/profle_template.xml",
        "views/locations_students_templates.xml",
        "views/hardship_request_remplates.xml",
        "views/update_hardship_request_remplates.xml",
        "views/success_hardship_request_templates.xml",
        "views/error_request_template.xml",
        "views/preferred_setting_template.xml",
        "views/scce_profle_template.xml",
        "views/availability_template.xml",
        "views/show_ci_placement_offer_facility_templates.xml",
        "views/show_scce_placement_offer_facility_templates.xml",
        "views/scce_student_profile_template.xml",
        "views/ci_student_profile_template.xml",
        "views/show_facility_student_templates.xml",
        "views/attachment_request_templates.xml",
        "views/ptse3_templates.xml",
        "views/ci_profle_template.xml",
        "views/survey_templates_print.xml",
        #Report
        'report/report_action.xml',
        'report/ptce3_report_template.xml',
        "views/required_documents_templates.xml",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "website_base/static/lib/js/signature_pad.umd.min.js",
            "website_base/static/src/css/profile_user.css",
            "website_base/static/src/css/hardship_information.css",
            "website_base/static/src/scss/style.scss",
            "website_base/static/src/js/location_student.js",
            "website_base/static/src/js/location_student_hard_ship.js",
            "website_base/static/src/js/location_student_update_hard_ship.js",
            "website_base/static/src/js/file.js",
            "website_base/static/src/js/state_hardship.js",
            "website_base/static/src/js/website_update_student_information.js",
            "website_base/static/src/js/website_update_scce_information.js",
            "website_base/static/src/js/departments.js",
            "website_base/static/src/js/attachment_request.js",
            "website_base/static/src/js/state_attachment_request.js",
            "website_base/static/src/js/signature_cpdm.js",
            "website_base/static/src/js/required_document.js",
            "website_base/static/src/js/scce_attachment_request.js",
            "website_base/static/src/js/website_update_ci_information.js",
            "website_base/static/src/js/file_attachment_request.js",
            "website_base/static/src/js/ptse3_student_details.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
    
}
