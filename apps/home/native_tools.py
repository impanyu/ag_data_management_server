from requests_oauthlib import OAuth2Session
import requests
import json
import os

import zipfile



def get_JD_authorization_code(path,request):
    global oauth2_session
    global TOKEN_GRANT_URL
    global CLIENT_SECRET
    global CLIENT_ID
    global CLIENT_REDIRECT_URI
    

    parent_path = os.path.dirname(path)
    #remove the first part before the first slash
    parent_path = parent_path.split('/',2)[2]
    CLIENT_ID = '0oabqi3ic7ZFEZE3z5d7'
    CLIENT_SECRET = 'eqkbTdRS9t2Eq1VWsqorB_PGKZdk4NiaO0u3bCucSaXVbIIlb9w9hn0Ysco9nYR2'
    CLIENT_REDIRECT_URI = f'http://unladma.hopto.org/files.html?current_path={parent_path}'
    CLIENT_REDIRECT_URI = f'http://unladma.hopto.org/api/get_JD_access_token/'
    

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
    request.session['oauth2_session'] = oauth2_session
    authorization_request, state = oauth2_session.authorization_url(AUTHORIZATION_URL, STATE)
    print("Click on the following link to present the user with sign in form where they authenticate and approve access to your application.")
    print(authorization_request) 
    return authorization_request

def get_JD_token(authorization_code,request):
    # Update the authorization code here
    AUTHORIZATION_CODE = authorization_code
    oauth2_session = request.session['oauth2_session']  

    # Now that we have an authorization code, let's fetch an access and refresh token
    token_response = oauth2_session.fetch_token(TOKEN_GRANT_URL, code=AUTHORIZATION_CODE, client_secret=CLIENT_SECRET)
    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']

    # Also take note that the access token expiration time is returned.  When the access token expires, 
    # you will want to use the refresh token to request a new access token (described later in this notebook)
    access_token_expiration = token_response['expires_in']

    print("Access Token: " + access_token)
    print("Refresh Token: " + refresh_token)
    print("Hours Token Is Valid: " + str(int(access_token_expiration/60/60)))

    # Leave the line below as-is. This is to make sure that you have update the AUTHORIZATION_CODE
    assert(AUTHORIZATION_CODE != 'place_authorization_code_here'), 'The AUTHORIZATION_CODE in this cell must be replaced by the authorization_code that you recieved'


def get_JD_organizations():
    global MYJOHNDEERE_V3_JSON_HEADERS
    MYJOHNDEERE_V3_JSON_HEADERS = { 'Accept': 'application/vnd.deere.axiom.v3+json',
                                'Content-Type': 'application/vnd.deere.axiom.v3+json'}
    # Now that we have an access token, let's use it to get a list of organizations that the user has access to
    ORGANIZATIONS_URL = 'https://sandboxapi.deere.com/platform/organizations'
    
    organizations_response = oauth2_session.get(ORGANIZATIONS_URL,headers=MYJOHNDEERE_V3_JSON_HEADERS)


    organizations = organizations_response.json()

    connections_link = None

    for link_object in organizations['values']:
        for links in link_object['links']:
            if(links['rel'] == 'connections'):
                connections_link = links['uri']
                break
    
    if (not connections_link == None):
        
        url = connections_link + "&redirect_uri=" + CLIENT_REDIRECT_URI
        return url
    else:
       
        return None

def populate_JD_dir(file_path,token):
    #populate file path 
    ORGANIZATIONS_URL = 'https://sandboxapi.deere.com/platform/organizations'
    organiations = get_myjohndeere_api_collection_json_response(oauth_session=oauth2_session, myjohndeere_uri=ORGANIZATIONS_URL, headers=MYJOHNDEERE_V3_JSON_HEADERS, params=None)
    for org in organiations['values']:
        #create a file for each organization
        org_name = org['name']
        org_id = org['id']
        org_path = file_path + "/" + org_name
        # if file does not exist, create it
        if not os.path.exists(org_path):
            os.makedirs(org_path)
        #get the fields for the organization
        ORGANIZATION_FIELDS_URL = org['links']['fields']
        fields = get_myjohndeere_api_collection_json_response(oauth_session=oauth2_session, myjohndeere_uri=ORGANIZATION_FIELDS_URL, headers=MYJOHNDEERE_V3_JSON_HEADERS, params=None)
        #create a file for each field
        for field in fields['values']:
            field_name = field['name']
            field_id = field['id']
            field_path = org_path + "/" + field_name
            # if file does not exist, create it
            if not os.path.exists(field_path):
                os.makedirs(field_path)
            '''
            for year in range(2020,2025):
               if not os.path.exists(field_path + "/" + str(year)):
                   os.makedirs(field_path + "/" + str(year))
               for operation in ["Aerial_Imagery","GHG","Planting","Soil_Sampling","Presciption_File","Treatment_Polygons","Tillage"]:
                    if not os.path.exists(field_path + "/" + str(year) + "/" + operation):
                        os.makedirs(field_path + "/" + str(year) + "/" + operation)
            '''
            FIELD_OPERATIONS_URL = field['links']['fieldOperation']
            field_operations = get_myjohndeere_api_collection_json_response(oauth_session=oauth2_session, myjohndeere_uri=FIELD_OPERATIONS_URL, headers=MYJOHNDEERE_V3_JSON_HEADERS, params=None)
            
            for field_operation in field_operations['values']:
                operation_type = field_operation['fieldOperationType']
                year =  field_operation['cropSeason']
                current_folder = field_path + "/" + str(year) + "/" + operation_type
                if not os.path.exists(current_folder):
                    os.makedirs(current_folder)
                 
                #get the files for each operation
                FILES_URL = field_operation['links']['shapeFileAsync']
                #query files url using python requests package
                files_response = requests.get(FILES_URL, headers=MYJOHNDEERE_V3_JSON_HEADERS)
                #get the status
                while files_response.status_code == 202:
                    files_response = requests.get(FILES_URL, headers=MYJOHNDEERE_V3_JSON_HEADERS)

                #get the headers
                headers = files_response.headers
                #print("status code is"+ str(files_response.status_code),flush=True)
                #print(FILES_URL,flush=True)
                #print response body
                #print(files_response.text,flush=True)
                
                if files_response.status_code == 200:
                    

                    #file_location =  headers['Location']
                    #download the file
                    #file_data = oauth2_session.get(file_location, headers=MYJOHNDEERE_V3_JSON_HEADERS)
                    with open(current_folder + "/shapefile.zip", 'wb') as f:
                        f.write(files_response.content)
                    #unzip the file
                   
                    with zipfile.ZipFile(current_folder + "/shapefile.zip", 'r') as zip_ref:
                        zip_ref.extractall(current_folder)
                    #delete zip file
                    #os.remove(current_folder + "/shapefile.zip")
                    

    return None



def convert_links_array_to_dictionary(links_a):
    link_dict = dict()
    for link_o in links_a:
        key = link_o['rel']
        value = link_o['uri']
        link_dict[key] = value
    return link_dict


def replace_links_as_object_array_with_links_as_dictionary(object_with_links_to_convert):
  object_with_links_converted = object_with_links_to_convert
  object_with_links_converted['links'] = convert_links_array_to_dictionary(object_with_links_to_convert['links'])
  return object_with_links_converted

def get_myjohndeere_api_json_response(oauth_session, myjohndeere_uri, headers , params = None):
  json_response = oauth2_session.get(myjohndeere_uri, headers = headers, params = params).json()
  return replace_links_as_object_array_with_links_as_dictionary(json_response)

def get_myjohndeere_api_collection_json_response(oauth_session, myjohndeere_uri, headers, params = None):
  collection_json_response = get_myjohndeere_api_json_response(oauth_session, myjohndeere_uri, headers, params)
  values_from_collection = collection_json_response['values']
  values_to_add_back_to_collection = []
  for object in values_from_collection:
    values_to_add_back_to_collection.append(replace_links_as_object_array_with_links_as_dictionary(object))
  collection_json_response['values'] = values_to_add_back_to_collection
  return collection_json_response

def get_myjohndeere_api_collection_values_for_all_pages(oauth_session, myjohndeere_uri, headers , params = None):
  collection_response = get_myjohndeere_api_collection_json_response(oauth_session, myjohndeere_uri, headers, params)
  collection_links = collection_response['links']
  while 'nextPage' in collection_links:
    next_page_response = get_myjohndeere_api_collection_json_response(oauth_session, collection_links['nextPage'], headers, params)
    collection_links = next_page_response['links']
    collection_response['values'].extend(next_page_response['values'])
  return collection_response['values']