# OAuth2 Provider

## Introduction

Our OAuth 2.0 provider product offers a robust and scalable solution for implementing secure authorization in applications. It enables seamless integration, allowing third-party services to access user data with fine-grained permissions while maintaining the highest standards of privacy and authentication. Our product simplifies the implementation of OAuth 2.0, providing developers with a reliable and customizable solution for enhancing the security of their applications.

### We provide four different types Grant Type:

 1. **Authorization Code Grant:** Ideal for web applications, this flow involves obtaining an authorization code that is exchanged for an access token, enhancing security by keeping sensitive information confidential.

 2. **Implicit Grant:** Suited for browser-based applications, this flow directly issues access tokens to clients after user authentication, simplifying the process but requiring careful consideration of security implications.

 3. **Resource Owner Password Credentials Grant:** Allows clients to directly exchange user credentials for an access token, making it suitable for trusted clients but less preferable due to potential security risks.

 4. **Client Credentials Grant:** Designed for machine-to-machine authentication, this flow enables direct exchange of client credentials for an access token, ensuring efficient authorization between services without involving user credentials.

## How It Works:

### Authorization Code Grant:

<img src="assets/Oauth2-authorization-code-grant.png" class="img-fluid" alt="OAuth2 Authorization Code Grant"/>

**Note: For Authorization Code Grant, You Have To Define Controller at client-side for callback URL. Consider Sample Code Below Or you can use our odoo module which provide authorization code grant flow: https://apps.odoo.com/apps/modules/16.0/api_auth_oauth2/**

```python
    @http.route('/cb', methods=['GET'], type='http', auth='none', save_session=False, csrf=False)
    def oauth2_client_callback(self, **kwargs):
        """
        This is for client, testing purpose
        """
        if 'error' in kwargs:
            error = {
                'error': kwargs['error']
            }
            return Response(json.dumps(error), status=400)

        client_id = '<your client id>'
        client_secret = '<your client secret>'
        redirect_uri = 'https://easyapi.ekika.app/cb'
        scope = ['read','write','create','delete']
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
        token = oauth.fetch_token(
            'https://oauth-provider.ekika.app/oauth2/token',
            authorization_response=request.httprequest.url, include_client_id=True)
        # Note: token['scope'] responded as list ["read", "write", "create", "delete"]
        # but client has to store string of space saperated like "read write create delete"
        return Response(json.dumps(token), status=200)
```

### Implicit Grant:

<img src="assets/Oauth2-Implicit-Grant.png" class="img-fluid" alt="OAuth2 Implicit Grant"/>

### Resource Owner Password Credential Grant:

<img src="assets/Oauth2-Resource-Owner-Password-Credential-Grant.png" class="img-fluid" alt="OAuth2 Resource Owner Password Credential Grant"/>


### Client Credential Grant:

<img src="assets/Oauth2-Client-Credential-Grant.png" class="img-fluid" alt="OAuth2 Client Credential Grant"/>

### Refresh Access Token:

<img src="assets/Oauth2-Refresh-Token.png" class="img-fluid" alt="OAuth2 Refresh Access Token"/>

### Token Revocation:

<img src="assets/Oauth2-Token-Revocation.png" class="img-fluid" alt="OAuth2 Token Revocation"/>

### Screenshots

<img src="assets/OAuth2-Demo.png" class="img-fluid" alt="OAuth2 Demo"/>
