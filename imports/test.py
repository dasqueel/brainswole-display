from rauth import OAuth2Service

fitbit = OAuth2Service(
    client_id='229DZQ',
    client_secret='a7a3b415cd5847f4835ed61b3f425022',
    name='fitbit',
    authorize_url='https://www.fitbit.com/oauth2/authorize',
    access_token_url='https://www.fitbit.com/oauth2/access_token',
    base_url='https://api.fitbit.com/')

# the return URL is used to validate the request
params = {'redirect_uri': 'http://127.0.0.1:5000/import',
          'response_type': 'code'}
url = fitbit.get_authorize_url(**params)

# once the above URL is consumed by a client we can ask for an access
# token. note that the code is retrieved from the redirect URL above,
# as set by the provider
data = {'code': 'foobar',
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://127.0.0.1:5000/import'}
session = fitbit.get_auth_session(data=data)
#session = service.get_auth_session(data=data)