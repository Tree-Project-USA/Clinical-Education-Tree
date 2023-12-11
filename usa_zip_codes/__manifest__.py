{
    "name": "USA Zipcode Data",
    "author": "Nomowsoft",
    "version": "16.0.1.0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "clinical_decision_making",
    ],
    # always loaded
    "data": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    'post_init_hook': 'add_geographical_data'
    
}
