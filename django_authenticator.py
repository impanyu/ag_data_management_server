import requests
from jupyterhub.auth import Authenticator
from tornado import gen


from bs4 import BeautifulSoup



class DjangoAuthenticator(Authenticator):

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        password = data['password']

        # URL of your Django application's authentication endpoint
        auth_url = "http://unlagdatamanagement.hopto.org/api/authenticate/"

        # Replace with the URL of your Django login page
        login_url = "http://localhost/login/"

        # Make a GET request to the login page to get the CSRF token
        response = requests.get(login_url)
        soup = BeautifulSoup(response.content, "html.parser")
        csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

        #csrf_token = 'token_value'
        headers = {'X-CSRFToken': csrf_token}

        response = requests.post(auth_url, headers = headers, data={"username": username, "password": password})
        print(response.status_code)

        if response.status_code == 200:
            return username
        else:
            return None
