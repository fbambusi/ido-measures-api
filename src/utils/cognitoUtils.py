import os
import json
import boto3
from botocore.config import Config


def get_client():
    my_config = Config(
        region_name='eu-central-1',

    )
    uip = ("a/a/"+os.environ.get("COGNITO_POOL", 'eu-central-1_sPMQnKBGz')).split("/")[-1]
    client = boto3.client('cognito-idp', config=my_config)
    return client, uip


attribute_names_in_cognito_to_attribute_names_in_response = {
    "custom:pots": {"rep_name": "pots", "default_value": "[]", "old_name": "pots"},
    "custom:accepted_t_c": {"rep_name": "accepted_terms_and_conditions", "default_value": "REJECTED",
                            "old_name": "accepted_conditions"},
    "custom:accepted_profilation": {"rep_name": "accepted_profilation", "default_value": "REJECTED",
                                    "old_name": "accepted_profilation"},
    "custom:accepted_marketing": {"rep_name": "accepted_marketing", "default_value": "REJECTED",
                                  "old_name": "accepted_marketing"},
    "custom:has_sensors": {"rep_name": "has_sensors", "default_value": "FALSE",
                                  "old_name": "hasAssociatedPots"}

}


def get_current_conito_user(user_id):
    client, pool_id = get_client()

    response = client.admin_get_user(
        UserPoolId=pool_id,
        Username=user_id
    )
    return response,client
def get_user_rep(user_id):

    response,client=get_current_conito_user(user_id)
    rep = {"id": f"users/{user_id}"}
    for att_name, features in attribute_names_in_cognito_to_attribute_names_in_response.items():
        val = get_attribute_from_cognito_response(response, att_name, features["default_value"])
        rep[features["rep_name"]] = val
    rep["pots"] = json.loads(rep["pots"])
    return rep


def get_attribute_from_cognito_response(cognito_response, attribute_name, default_value="REJECTED"):
    atts = cognito_response["UserAttributes"]
    elems = list(filter(lambda p: p["Name"] == attribute_name, atts))
    if elems:
        return elems[0]["Value"]
    return default_value
