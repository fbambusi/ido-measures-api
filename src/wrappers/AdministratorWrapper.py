import json

def admin_lambda_wrapper(func):
    def admin_wrapper(*args, **kwargs):
        event=args[0]
        #print(event["cognitoPoolClaims"]["groups"][0])
        is_authorized=event["cognitoPoolClaims"]["groups"].find("ido-admins-"+event["stage"])>=0
        if is_authorized:
            resp=func(*args, **kwargs)
            return resp
        else:
            resp={"statusCode": 403,
                    "body": json.dumps({"message": "You need administrator privileges to access this resource."
                    "Please contact us at software.issues@wiseair.vision"}),
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"}}
            return  resp



    return admin_wrapper