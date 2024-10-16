# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: www.ekikacorporation.com). #
# See LICENSE file for full copyright and licensing details.                     #
#                                                                                #
##################################################################################

{
    'name': 'OAuth2 Provider',
    'summary': 'The "OAuth2 Provider for Odoo" module enhances the functionality of the Odoo ERP system by transforming it into an OAuth2 provider.',
    'company': 'EKIKA CORPORATION PRIVATE LIMITED',
    'author': 'EKIKA',
    'website': 'https://ekika.co',
    'category': 'Productivity,Extra Tools,Tools',
    'version': '16.0.1.1',
    'license': 'OPL-1',
    'depends': ['base', 'web', 'ekika_utils'],
    'external_dependencies': {
        'python': ['oauthlib==3.2.2'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/oauth2_client.xml',
        'views/oauth2_authorization_code.xml',
        'views/oauth2_token.xml',
        'views/menus.xml',
        'templates/oauth2_authorization.xml'
    ],
    'assets': {},
    'images': ['static/description/banner.png'],
    'price': 43.00,
    'currency': 'EUR',
    'description': """
The "OAuth2 Provider for Odoo" module enhances the functionality of the Odoo ERP system by transforming it into an OAuth2 provider. OAuth2 is a widely used protocol for secure and delegated access to resources on the web. With this module, Odoo can now serve as an authentication and authorization server, allowing external applications and services to securely access Odoo resources on behalf of users.

Key Features:

OAuth2 Authorization Server:

Odoo is equipped with OAuth2 capabilities, enabling it to generate access tokens and refresh tokens for external applications.
Implements the authorization endpoint to handle user consent for data access.
User Authentication:

Enables users to authenticate themselves using their Odoo credentials when authorizing external applications.
Ensures secure and standardized authentication processes following the OAuth2 protocol.
Token Generation:

Grants access tokens to authorized external applications, allowing them to access protected resources within Odoo.
Supports the generation of refresh tokens for long-term access, enhancing security and user experience.
Scopes and Permissions:

Defines and manages scopes to control the level of access granted to external applications.
Allows administrators to configure and customize permissions based on specific business requirements.
Token Expiry and Refresh:

Implements token expiration mechanisms to enhance security by limiting the lifespan of access tokens.
Supports token refresh functionality, allowing applications to obtain new access tokens without requiring user reauthentication.
User Consent Management:

Provides a user-friendly interface for users to review and manage the external applications that have been granted access to their Odoo data.
Ensures transparency and control over data sharing permissions.
Integration with Odoo Modules:

Seamlessly integrates with existing Odoo modules, ensuring compatibility with various Odoo functionalities.
Allows for the secure access of Odoo data from external applications without compromising system integrity.
Logging and Auditing:

Maintains comprehensive logs of OAuth2-related activities, aiding administrators in monitoring and auditing access to Odoo resources.
Extensibility:

Offers hooks and extension points for developers to customize and extend the functionality of the OAuth2 provider as needed.
By incorporating the "OAuth2 Provider for Odoo" module into your Odoo instance, you empower your organization to securely share data with external applications while maintaining control and transparency over user permissions. This module is designed to enhance the interoperability and extensibility of Odoo, making it a versatile solution for businesses with diverse integration requirements.
    """
}
