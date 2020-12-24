import boto3
import requests
import json

class IdoClient(object):
    email = None
    password = None
    app_client_id = None
    stage=None
    def __init__(self,email,password,app_client_id,stage="stage"):
        self.email=email
        self.password=password
        self.app_client_id=app_client_id
        self.stage=stage
        self._get_token()

    def _get_token(self):
        """
        Get bearer token to sign subsequent requests
        :return:
        """
        client = boto3.client('cognito-idp', region_name="eu-central-1")

        resp = client.initiate_auth(
            ClientId=self.app_client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                "USERNAME": self.email,
                "PASSWORD": self.password
            }
        )

        print("Log in success")
        print("Access token:", resp['AuthenticationResult']['AccessToken'])
        print("ID token:", resp['AuthenticationResult']['IdToken'])
        self.id_token=resp['AuthenticationResult']['IdToken']

    def authenticated_get(self,url):
        """
        Perform a GET request, signing it with the internal bearer token
        :param url:
        :return:
        """
        resp = requests.get(url=url,
                            headers={"Authorization": "Bearer " + self.id_token})
        return resp.content

    def authenticated_post(self,url,payload):
        """
        Perform a POST request, signing it with the internal bearer token
        :param url:
        :return:
        """
        resp = requests.post(url=url,json=payload,
                            headers={"Authorization": "Bearer " + self.id_token})
        return resp.content

    def authenticated_patch(self,url,payload):
        """
        Perform a POST request, signing it with the internal bearer token
        :param url:
        :return:
        """
        resp = requests.patch(url=url,json=payload,
                            headers={"Authorization": "Bearer " + self.id_token})
        return resp.content

    def simple_post(self,url,payload):
        """
        Perform a POST request with JSON content
        :param url:
        :return:
        """
        resp = requests.post(url=url,json=payload,
                            )
        return resp.content

    def legacy_post(self,url,payload):
        """
        Perform a POST request with JSON content
        :param url:
        :return:
        """
        resp = requests.post(url=url,params=payload,
                            )
        return resp.content

    def get_sensor_from_chip_id(self,chip_id):
        if self.stage=="prod":
            url="https://apiv1.ido.wiseair-api.com/sensors?chip_id={chip_id}".format(chip_id=chip_id)
        else:
            url = "https://apiv1-stage.ido.wiseair-api.com/sensors?chip_id={chip_id}".format(chip_id=chip_id)
        resp=self.authenticated_get(url=url)
        try:
            return json.loads(resp.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            return {}