import logging
import os
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, Float, GeoPoint, Boolean,connections
from elasticsearch import  RequestsHttpConnection
import boto3
from requests_aws4auth import AWS4Auth
import requests
import json

if len(logging.getLogger().handlers) > 0:
    # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
    # `.basicConfig` does not execute. Thus we set the level directly.
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

class ElasticsearchUtils(object):

    """
    To run this class locally, execute
    docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.9.3
    to start a local elasticsearch instance.

    To connect to kibana, execute
    sudo npm install -g aws-es-kibana
    AWS_PROFILE=default aws-es-kibana search-wiseair-es-vxt5w4gpvoq237sczmrfvaw5ou.eu-south-1.es.amazonaws.com
    and visit the suggested address
    """

    _stage=None
    _host=None
    _port=None
    _region=None
    _service="es"
    connections=None

    @staticmethod
    def get_stage_name():
        try:
            return os.getenv('STAGE_NAME')
        except ValueError as environmentVariableNotFound:
            return "local"


    def __init__(self,region = "eu-south-1"):
        stage=ElasticsearchUtils.get_stage_name()
        self._stage=stage
        self._region=region
        if stage=="prod" or stage=="stage":
            self._host=os.environ.get("ES_ENDPOINT","search-ido-es-observations-stage-nbcnoqypzren6t37gshyo2wv4a.eu-south-1.es.amazonaws.com")
            self._port=443
        else:
            self._host = os.environ.get("ES_ENDPOINT",
                                    "localhost")
            self._port=9200
        self.connections=self.initialize_elasticsearch()

    def initialize_elasticsearch(self):
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, self._region, self._service,
                           session_token=credentials.token)
        secure_connection=self._stage in ["prod","stage"]
        connections.configure(
            default={"hosts": [{"host": self._host, "port": self._port, }],
                     "http_auth": awsauth, "use_ssl": secure_connection, "verify_certs": secure_connection, "connection_class": RequestsHttpConnection, }
            )

        connections.get_connection()

    def drop_index(self,index_name):
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, self._region, self._service,
                           session_token=credentials.token)
        r = requests.delete('https://' + self._host + "/" + index_name, auth=awsauth)

    def index_exists(self, index_name):
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, self._region, self._service,
                           session_token=credentials.token)
        r = requests.head('https://' + self._host + "/" + index_name, auth=awsauth)
        return r.status_code==200
        print(r.content)


    def reindex(self,data_source_index_name,data_destination_index_name):
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, self._region, self._service,
                           session_token=credentials.token)
        r = requests.post('https://' + self._host + "/_reindex", auth=awsauth,
                          json={
                              "source": {
                                  "index": data_source_index_name
                              },
                              "dest": {
                                  "index": data_destination_index_name
                              }
                          })

    def get_info_on_index(self,index_name):
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, self._region, self._service,
                           session_token=credentials.token)
        r = requests.get('https://' + self._host + "/" + index_name+"/_count", auth=awsauth)
        return json.loads(r.content)["count"]
        pass

    class QueryKeyWords(object):
        START_DATETIME="start_datetime"
        END_DATETIME="end_datetime"
        LATITUDE="lat"
        LONGITUDE="lon"
        PAGE="page"
        ITEMS="items"