from requests_oauthlib import OAuth2Session
import requests
import json
import os


def connect_JD(path):
    parent_path = os.path.dirname(path)
    #remove the first part before the first slash
    parent_path = parent_path.split('/',2)[2]
    CLIENT_ID = '0oabqi3ic7ZFEZE3z5d7'
    CLIENT_SECRET = 'eqkbTdRS9t2Eq1VWsqorB_PGKZdk4NiaO0u3bCucSaXVbIIlb9w9hn0Ysco9nYR2'
    CLIENT_REDIRECT_URI = f'http://unladma.hopto.org/files.html?current_path={parent_path}'

    # Leave the line below as-is. This line of code verifies that you've modified the CLIENT_ID, CLIENT_SECRET, CLIENT_REDIRECT_URI to the values above so that your application can complete OAuth"
    assert(CLIENT_ID != 'place_client_key_here' and CLIENT_SECRET != 'place_client_secret_here' and CLIENT_REDIRECT_URI != 'place_client_redirect_uri_here'), "You need to update your CLIENT_ID, CLIENT_SECRET, or CLIENT_REDIRECT_URI in this cell"

    WELL_KNOWN_URL = 'https://signin.johndeere.com/oauth2/aus78tnlaysMraFhC1t7/.well-known/oauth-authorization-server'

    # Query the ./well-known OAuth URL and parse out the authorization URL, the token grant URL, and the available scopes
    well_known_response = requests.get(WELL_KNOWN_URL)
    well_known_info = json.loads(well_known_response.text)

    AUTHORIZATION_URL = well_known_info['authorization_endpoint']
    TOKEN_GRANT_URL = well_known_info['token_endpoint']
    AVAILABLE_SCOPES = str(' ').join(well_known_info['scopes_supported'])

    print('Well Known Authorization URL - ' + AUTHORIZATION_URL)
    print('Well Known Token Grant URL - ' + TOKEN_GRANT_URL)
    print('Available Scopes - ' + AVAILABLE_SCOPES)

    SCOPES_TO_REQUEST = {'org2', 'files', 'offline_access','ag3','eq2', 'work2'}
    STATE = "1234"
    oauth2_session = OAuth2Session(CLIENT_ID,  redirect_uri=CLIENT_REDIRECT_URI, scope=SCOPES_TO_REQUEST)

    authorization_request, state = oauth2_session.authorization_url(AUTHORIZATION_URL, STATE)
    print("Click on the following link to present the user with sign in form where they authenticate and approve access to your application.")
    print(authorization_request) 
    return authorization_request

def get_JD_token(authorization_code):
    # Update the authorization code here
    AUTHORIZATION_CODE = authorization_code

    # Leave the line below as-is. This is to make sure that you have update the AUTHORIZATION_CODE
    assert(AUTHORIZATION_CODE != 'place_authorization_code_here'), 'The AUTHORIZATION_CODE in this cell must be replaced by the authorization_code that you recieved'
