import json
from src.wrappers.EmailOnFailureDecorator import email_on_failure


def event_context_processor(event, context):
    """
    The core logic of lambda function.
    :param event:
    :param context:
    :return: a CORS-compliant HTTP response.
    """
    return {"statusCode": 200,
            "body": json.dumps({"sender": "hello2"}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"}}


@email_on_failure
def prod_lambda(event, context):
    """
    The core logic of the lambda function, wrapped with monitoring utilities.
    :param event:
    :param context:
    :return: HTTP response produced by the core logic
    """
    return event_context_processor(event, context)


def lambdaHandler(event, context):
    return prod_lambda(event, context)
