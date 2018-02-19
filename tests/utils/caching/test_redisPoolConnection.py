from unittest import TestCase

from framework.utils.caching.redis_pool import RedisPoolConnection


class TestRedisPoolConnection(TestCase):

    def setUp(self):

        config = {
            'host': 'localhost',
            'port': 6379,
            'password': None,
            'db_number': None,
            'max_connections': 2
        }

        try:
            self.redis_connection = RedisPoolConnection(**config)
        except Exception as exc:
            raise exc

    def tearDown(self):
        del self.redis_connection

    def test_set(self):
        key = 'key1'
        value = 'value1'
        response = self.redis_connection.set(key=key, value=value)
        self.assertTrue(response)

    def test_set_with_namespace(self):
        key = 'key1'
        value = 'value1'
        namespace = 'N'
        delimiter = '/'
        response = self.redis_connection.set(namespace=namespace, delimiter=delimiter, key=key, value=value)
        self.assertTrue(response)

    def test_hm_set(self):
        name_of_hash_map = 'hash_map'
        hash_map = {
            'key1': 'value1',
            'key2': 'value2',
        }
        response = self.redis_connection.hm_set(name=name_of_hash_map, hash_map=hash_map)
        self.assertTrue(response)

    def test_hm_set_with_exception(self):
        name_of_hash_map = 'hash_map'
        hash_map = 10
        self.assertRaises(Exception, self.redis_connection.hm_set, name=name_of_hash_map, hash_map=hash_map)

    def test_get_with_namespace(self):
        key = 'key1'
        value = 'value1'
        namespace = 'N'
        delimiter = '/'
        self.redis_connection.set(namespace=namespace, delimiter=delimiter, key=key, value=value)
        response = self.redis_connection.get(namespace=namespace, delimiter=delimiter, key=key)
        self.assertIsNotNone(response)
        self.assertEqual(response, 'value1')

    def test_get(self):
        key = 'key1'
        value = 'value1'
        self.redis_connection.set(key=key, value=value)
        response = self.redis_connection.get(key=key)
        self.assertEqual(response, 'value1')

    def test_get_all_keys_values(self):
        for i in range(0, 1000):
            key = 'key-' + str(i)
            value = 'value-' + str(i)
            self.redis_connection.set(namespace='test', key=key, value=value)
        response = self.redis_connection.get_all_keys_values(regex='test*')
        response_list = list(response)
        self.assertEqual(len(response_list), 1000)

    def test_get_all_hash_maps(self):
        namespace = 'all_hash_maps'
        for i in range(0, 10):
            hash_map_name = 'name' + str(i)
            hash_map = {
                'key'+ str(i): 'value' + str(i)
            }
            response = self.redis_connection.hm_set(name=hash_map_name, hash_map=hash_map, namespace=namespace)
            self.assertTrue(response)
        response = self.redis_connection.get_all_hash_maps(regex='all_hash_maps:*')
        response_list = list(response)
        self.assertEqual(len(response_list), 10)














