import boto3
import os
import datetime
from boto3.dynamodb.conditions import Key
import random
import string
import json
import decimal


class DynamoStorableObject(object):
    """ An object that can be stored on DynamoDb

    :cvar _VISIBLE_PARAMETERS: the properties that will be persisted into DynamoDB
    :cvar _PUBLIC_PARAMETERS: the properties that will be showed externally, e.g., in HTTP responses.

    """
    HASH_KEY_NAME = "hashKey"
    SORT_KEY_NAME = "sortKey"

    FORBIDDEN_SEPARATOR = "+++"

    DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S"


    _VISIBLE_PARAMETERS = []
    _PUBLIC_PARAMETERS = []

    __PARAMS = ["wise_id"]

    _hashKey = None
    _sortKey = None
    _created_at = None

    @staticmethod
    def getTable():
        """Get the name of DynamoDB table to use
        Check environment variable DATABASE_TABLE, and return an hardcoded value on failure.
        :return:
        """
        dynamodb = boto3.resource('dynamodb')
        try:
            tableName = os.getenv('DATABASE_TABLE')
            table = dynamodb.Table(tableName)
        except ValueError as environmentVariableNotFound:
            table = dynamodb.Table("ido-weather-cache-stage")
        return table

    def __init__(self):
        self._created_at = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, value_of_created_at):
        self._created_at = value_of_created_at

    @property
    def sortKey(self):
        return self._sortKey

    @property
    def hashKey(self):
        return self._hashKey

    @property
    def wise_id(self):
        """ DynamoDB id of object
        The combination of hashKey and sortKey, univocally identifies objects.
        :return:
        """
        return str(self._hashKey) + DynamoStorableObject.FORBIDDEN_SEPARATOR + str(self._sortKey)

    @wise_id.setter
    def wise_id(self, wise_id_value):
        """
        Set the hash key and the sort key of an object starting from a known wise_id, i.e., the combination of
        hashKey and sortKey
        :param wise_id_value:
        :return:
        """
        self._hashKey = wise_id_value.split(DynamoStorableObject.FORBIDDEN_SEPARATOR)[0]
        self._sortKey = wise_id_value.split(DynamoStorableObject.FORBIDDEN_SEPARATOR)[1]

    def set_representation(self, dictionaryOfAttributes):
        for name in self._VISIBLE_PARAMETERS:
            setattr(self, name, dictionaryOfAttributes[name])

    def decimal_default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        raise TypeError

    def get_representation(self):
        """
        Obtain a dictionary that represents the object.
        :return:
        """
        partial_dictionary = {}
        # print("getting representaion")
        for name in self.__class__._VISIBLE_PARAMETERS + DynamoStorableObject.__PARAMS:
            partial_dictionary[name] = getattr(self, name)

        return json.loads(json.dumps(partial_dictionary, default=self.decimal_default))

    def get_public_representation(self):
        """
        Get a JSON representation of the object, setting only the parameters identified as publicly visible
        :return:
        """
        dict = {}
        for name in self.__class__._PUBLIC_PARAMETERS:
            # dict[name] = getattr(self, "_" + name)
            dict[name] = getattr(self, name)
            # print("getting {}:{}".format(name,dict[name]))

        return json.loads(json.dumps(dict, default=self.decimal_default))

    def get_public_representation(self):
        """
        Get a JSON representation of the object, setting only the parameters identified as publicly visible
        :return:
        """
        dict = {}
        for name in self.__class__._PUBLIC_PARAMETERS:
            # dict[name] = getattr(self, "_" + name)
            dict[name] = getattr(self, name)
            # print("getting {}:{}".format(name,dict[name]))

        return json.loads(json.dumps(dict, default=self.decimal_default))


    def fetch_from_dynamo(self):
        table = DynamoStorableObject.getTable()
        # print("retrieving from dynamo using HK: {} and SK:{}".format(self._hashKey, self._sortKey))

        response = table.query(
            KeyConditionExpression=Key(self.HASH_KEY_NAME).eq(self.hashKey) & Key(self.SORT_KEY_NAME).eq(self.sortKey)
        )
        items = response['Items']
        if items:
            res = self.set_representation(items[0])
        else:
            res = []
        return res

    @property
    def hashKeyOnsecondaryIndex(self):
        return {"hash_key_name": "", "hash_key_value": ""}

    @property
    def sortKeyOnsecondaryIndex(self):
        return {"sort_key_name": "", "sort_key_value": ""}

    def fetch_from_secondary_index(self):
        """
        Fetch from dynamoDB using the secondary index
        :return:
        """
        table = DynamoStorableObject.getTable()

        hk_on_secondary_index = self.hashKeyOnsecondaryIndex
        sk_on_secondary_index = self.sortKeyOnsecondaryIndex
        response = table.query(
            IndexName="secondaryIndex",
            KeyConditionExpression=Key(hk_on_secondary_index["hash_key_name"]).eq(
                hk_on_secondary_index["hash_key_value"]) & Key(sk_on_secondary_index["sort_key_name"]).eq(
                sk_on_secondary_index["sort_key_value"])
        )
        items = response['Items']
        if items:
            res = self.set_representation(items[0])
        else:
            res = []
        return res


    @classmethod
    def get_objects_from_representations(cls,iterable_of_representations):
        ret = []
        for it in iterable_of_representations:
            try:
                obj = cls()
                obj.set_representation(it)
                ret.append(obj)
            except:
                pass
        return ret

    @classmethod
    def fetch_from_secondary_index_hash_key(cls,hash_key_value):
        """
        Fetch from dynamoDB using the secondary index, using only the hash key
        :return:
        """
        table = DynamoStorableObject.getTable()

        hk_on_secondary_index = cls().hashKeyOnsecondaryIndex
        response = table.query(
            IndexName="secondaryIndex",
            KeyConditionExpression=Key(hk_on_secondary_index["hash_key_name"]).eq(
                hash_key_value)
        )
        items = response['Items']
        return cls.get_objects_from_representations(items)

    @classmethod
    def get_all(cls,exclusive_start_key):
        """
        Fetch all the items in the table, and return the ones that belong to the class.
        :param exclusive_start_key:
        :return:
        """
        table = DynamoStorableObject.getTable()
        if exclusive_start_key is not None:
            response = table.scan(ExclusiveStartKey=exclusive_start_key
            )
        else:
            response = table.scan()
        items = response['Items']
        return cls.get_objects_from_representations(items),response.get("LastEvaluatedKey",None),response.get("Count",0)

    def store_to_dynamo(self):
        """
        Store all the attributes that belong to the _VISIBLE_PARAMETERS array to DynamoDB
        :return:
        """

        table = DynamoStorableObject.getTable()
        dic = self.get_representation()
        for k, val in dic.items():
            if isinstance(val, float):
                if round(val, 2) == val:
                    dic[k] = decimal.Decimal(str(val))
                else:
                    dic[k] = str(val)
        dic["updated_at"] = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        dic[DynamoStorableObject.HASH_KEY_NAME] = self.hashKey
        dic[DynamoStorableObject.SORT_KEY_NAME] = self.sortKey
        response = table.put_item(
            Item=dic
        )
        return response

    def remove_form_dynamo(self):
        """
        Permanently delete the object from DynamoDB
        :return: the response provided by DynamoDB
        """
        table = DynamoStorableObject.getTable()
        response = table.delete_item(
            Key={self.HASH_KEY_NAME: self.hashKey, self.SORT_KEY_NAME: self.sortKey}
        )
        return response

    @staticmethod
    def get_raw_by_hash_key(hash_key_value):
        """ Get raw content from DynamoDB
        Get all the items in DynamoDB that have the given value of hash key.
        Results could be semantically and syntactically heterogeneous (e.g., if two document belonging to two different
        types have the same hash key)
        :param hash_key_value:
        :return:
        """
        table = DynamoStorableObject.getTable()
        response = table.query(
            KeyConditionExpression=Key(DynamoStorableObject.HASH_KEY_NAME).eq(hash_key_value)
        )
        items = response['Items']
        return items

    @classmethod
    def get_by_hash_key(cls, hash_key_value):
        """
        Get all the items with a specific hashKey, and return them as objects (not dictionaries).
        :param hash_key_value:
        :return:
        """
        items = DynamoStorableObject.get_raw_by_hash_key(hash_key_value)
        ret = []
        for it in items:
            try:
                obj = cls()
                obj.set_representation(it)
                ret.append(obj)
            except:
                pass
        return ret

    @classmethod
    def get_raw_by_hash_key_and_range_key(cls, hash_key_value, minSortKeyValue, maxSortKeyValue):
        """
        Get all the items with a specific hashKey and sortKey, and return them as objects (not dictionaries).
        :param hash_key_value:
        :return:
        """
        table = DynamoStorableObject.getTable()
        response = table.query(
            KeyConditionExpression=Key(DynamoStorableObject.HASH_KEY_NAME).eq(hash_key_value)
                                   &
                                   Key(DynamoStorableObject.SORT_KEY_NAME).between(minSortKeyValue, maxSortKeyValue)
        )
        items = response['Items']
        return items

    @staticmethod
    def to_datetime(dt):
        """
        Convert a string to datetime using ISO8061 standard
        :param dt:
        :return:
        """
        try:
            return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        except ValueError as e:
            return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
