{
    "name": "THEM CPDM",
    "summary": "THEM CPDM",
    "description": "",
    "author": "Ahmed Humran",
    "category": "Theme",
    "version": "16.0.1.0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "website",
    ],
    # always loaded
    "data": [
         # Snippets
        "views/snippets/s_carousels.xml",
        "views/snippets/s_text_image.xml",
        "views/snippets/s_text_image2.xml",
        "views/snippets/s_features.xml",
        "views/snippets/s_banar.xml",
        
        # Pages
        "views/pages/home.xml",    
    ],
    # only loaded in demonstration mode
    "demo": [],
    "assets": {
        "web._assets_primary_variables": [
            "them_cpdm/static/src/scss/primary_variables.scss",
            "them_cpdm/static/src/scss/color.scss",
        ],
        "web.assets_frontend": [
            "/them_cpdm/static/src/scss/property-agents.scss",
            "/them_cpdm/static/src/css/style.css",
        ],
    },
    "license": "LGPL-3",
    
}
