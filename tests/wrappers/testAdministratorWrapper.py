import unittest

from src.wrappers.AdministratorWrapper import admin_lambda_wrapper


@admin_lambda_wrapper
def protected_function(event, context):
    return {"statusCode": 200}


class TestCaseForcreateSensor(unittest.TestCase):
    """
    Test the invocation of a lambda with authorized and unauthorized users
    """

    def testAuthorizedAdminWrapper(self):
        """
        Invoke a function with an authorized user
        :return:
        """
        resp=protected_function({
            "cognitoPoolClaims": {"groups": "ido-admins-stage"},
            "stage": "stage",
            "path": {"sensor_id": "ari-0001"}}, {})
        self.assertEqual(resp["statusCode"],200)

    def testUnauthorizedAdminWrapper(self):
        """
        Invoke a function with an authorized user
        :return:
        """
        resp=protected_function({
            "cognitoPoolClaims": {"groups": "idoo-admins"},
            "stage": "stage",
            "path": {"sensor_id": "ari-0001"}}, {})
        self.assertEqual(resp["statusCode"],403)




