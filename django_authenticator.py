import requests
from jupyterhub.auth import Authenticator
from tornado import gen

class DjangoAuthenticator(Authenticator):

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        password = data['password']

        # URL of your Django application's authentication endpoint
        auth_url = "http://unlagdatamanagement.hopto.org/api/authenticate/"

        response = requests.post(auth_url, data={"username": username, "password": password})

        if response.status_code == 200:
            return username
        else:
            return None
