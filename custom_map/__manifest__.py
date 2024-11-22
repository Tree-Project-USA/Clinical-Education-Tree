# custom_map/__manifest__.py
{
    'name': 'Custom Map',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Add a custom map to the portal',
    'author': 'Your Name',
    'website': 'http://www.yourwebsite.com',
    'depends': ['website'],
    'data': [
        'views/custom_map_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_map/static/lib/leaflet.js',
            'custom_map/static/lib/leaflet.css',
            'custom_map/static/scss/*.scss',
            'custom_map/static/js/map.js',
        ],
    },
    'installable': True,
    'application': False,
}