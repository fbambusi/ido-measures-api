import boto3
import json
import __main__
import os



def send_error_email(fname, json_payload):
    """
    Send an email to contact@wiseair.vision in case a lambda function fails.
    The email contains the name of the function which failed, and the input which made it fail.
    :param fname:
    :param json_payload:
    :return:
    """
    client = boto3.client('ses', region_name="eu-west-1")
    stage = os.environ.get("STAGE_NAME", "stage")

    address = "fulvio.bambusi@wiseair.vision" if stage != "prod" else "contact@wiseair.vision"

    response = client.send_email(
        Destination={
            'ToAddresses': [
                address,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': 'Function {fname} has failed from service fname, with event / context {pload}'.format(
                        fname=fname, pload=json_payload),
                },
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': 'Function {fname} has failed from service fname, with event / context {pload}'.format(
                        fname=fname, pload=json_payload),
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'IDO:sensors-api function failure',
            },
        },
        Source='software.issues@wiseair.vision',

    )


def email_on_failure(func):
    """
    This wrapper is used to monitor lambda functions, and notify via email failures.
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        fname = str(__main__.__file__).split("/")[-1]
        print("Invoking " + str(fname))
        error_happened = False
        try:
            resp = func(*args, **kwargs)
            if 499 < resp["statusCode"] < 600:
                error_happened = True
        except NotImplementedError:
            error_happened = True
            resp = {"statusCode": 501,
                    "body": json.dumps({"message": "This operation is not supported yet. Please refer to ido.readme.io "
                                                   "to get a list of the currenlty supported operations."
                                                   }),
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"}}
        except FileNotFoundError:
            error_happened = True
            resp = {"statusCode": 500,
                    "body": json.dumps({"message": "Internal server error. Our IT has been notified, please ask "
                                                   "software.issues@wiseair.vision if you need urgent support. "
                                        }),
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"}}

        if error_happened:
            # context_error_string='Context: %s' %json.dumps(vars(*args[1]), cls=PythonObjectEncoder)
            body_string = f' Kwargs: {args}'
            send_error_email(fname=fname, json_payload=body_string)
        return resp

    return wrapper
