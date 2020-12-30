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
            "body": json.dumps({
                "data": [
                    {
                        "values": {
                            "pm1": {
                                "value": 30.59,
                                "unit": "ug/m3"
                            },
                            "pm2p5": {
                                "value": 35.86,
                                "unit": "ug/m3"
                            },
                            "pm4": {
                                "value": 38.71,
                                "unit": "ug/m3"
                            },
                            "pm10": {
                                "value": 39.28,
                                "unit": "ug/m3"
                            },
                            "relative_humidity": {
                                "value": 100.0,
                                "unit": "pc"
                            },
                            "temperature": {
                                "value": -1.14,
                                "unit": "celsius"
                            },
                            "pressure": {
                                "value": 990.0,
                                "unit": "hpa"
                            },
                            "rain_last_1h": {
                                "value": 0.0,
                                "unit": "mm"
                            },
                            "wind_speed": {
                                "value": 0.5,
                                "unit": "m/s"
                            },
                            "wind_direction": {
                                "value": 0.0,
                                "unit": "deg"
                            },
                            "cloud_coverage": {
                                "value": 75.0,
                                "unit": "pc"
                            }
                        },
                        "diagnostic": {
                            "rssi": {
                                "value": -56.0,
                                "unit": "dbm"
                            },
                            "measuring_time": {
                                "value": 11321,
                                "unit": "ms"
                            },
                            "connecting_time": {
                                "value": 5526,
                                "unit": "ms"
                            },
                            "battery": {
                                "value": 3.64,
                                "unit": "v"
                            }
                        },
                        "sensor_id": "/sensors/ari-1067",
                        "valid_at": "2020-12-29T01:30:18Z",
                        "display_address": "Antonio Panizzi",
                        "location": {
                            "latitude": 45.452341638193,
                            "longitude": 9.1372738294363,
                            "location_type": "ON_ROAD"
                        }
                    }
                ]
            }),
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
