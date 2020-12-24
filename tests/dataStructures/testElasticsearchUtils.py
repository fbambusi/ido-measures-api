
import unittest
from src.dataStructures.ElasticsearchUtils import ElasticsearchUtils

class MyTestCase(unittest.TestCase):
    def test_connection_to_local_instance_of_elasticsearch(self):
        eu=ElasticsearchUtils()



if __name__ == '__main__':
    unittest.main()
