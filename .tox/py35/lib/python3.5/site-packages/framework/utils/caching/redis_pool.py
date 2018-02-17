from itertools import zip_longest

from redis import ConnectionPool, Redis
from redis.exceptions import (ConnectionError, TimeoutError, WatchError)


class RedisPoolConnection:
    """
     connection pool to manage connections to a Redis server. By default, each Redis instance you create will
     in turn create its own connection pool. You can override this behavior and use an existing connection
     pool by passing an already created connection pool instance to the connection_pool argument of the
     Redis class.

     By default redis open 16 db's while creating connection. we can specify specific db number to open it.

    """
    def __init__(self, **kwargs):
        """
        create redis connection with pooling

        :Keyword Arguments:

        * *host* (``str``) -- hostname for redis
        * *port* (``str``) -- port for redis
        * *password* (``str``) -- password , Default None
        * *db_number* (``int``) -- db number from 0-15.
        * *max_connections* (``int``) -- maximum number of connections for pooling.

        """
        self._host = kwargs.get('host')
        self._port = kwargs.get('port')
        self._password = kwargs.get('password')
        self._db_number = kwargs.get('db_number')
        self._max_connections = kwargs.get('max_connections')
        self._connection = self._create_connection_with_pooling()

    def _create_connection_with_pooling(self):
        connection_pool = ConnectionPool(max_connections=self._max_connections, host=self._host, port=self._port, password=self._password, db=self._db_number, decode_responses=True)
        try:
            redis_client = Redis(connection_pool=connection_pool)
        except Exception as exc:
            raise exc
        return redis_client

    def set(self, key=None, value=None, namespace=None, delimiter=':'):
        """
        set the value for the given key

        :param key: key to set
        :type key: str
        :param value: value to set for a given key
        :type value: Any
        :param namespace: common prefix for set of keys, which uniquely identifies the set of keys from all keys.
        :type namespace: str
        :param delimiter: used in between joining namespace and key
        :type delimiter: str
        :return: return True if success else False
        :rtype: bool
        :raises ConnectionError, TimeoutError, Exception
        """
        delimiter = delimiter or ':'
        try:
            key = self.get_key_with_or_without_namespace(key=key, namespace=namespace, delimiter=delimiter)
            response = self._connection.set(key, value)
        except (ConnectionError, TimeoutError, Exception) as exc:
            raise exc
        return response

    def get(self, key=None, namespace=None, delimiter=':'):
        """
        returns the value based on key
        :param key: key to search
        :type key: str
        :param namespace: common prefix for set of keys, which uniquely identifies the set of keys from all keys.
        :type namespace: str
        :param delimiter: used in between joining namespace and key
        :type delimiter: str
        :return: value of the key
        :rtype: Any
        :raises ConnectionError, TimeoutError, Exception
        """
        delimiter = delimiter or ':'
        try:
            key = self.get_key_with_or_without_namespace(key=key, namespace=namespace, delimiter=delimiter)
            value = self._connection.get(key)
        except (ConnectionError, TimeoutError, Exception) as exc:
            raise exc
        return value

    def get_all_keys_values(self, regex='*'):
        """
        returns all the keys. if we specify the namespace it will get from that namespace.
        :param regex: regex for identifying the keys
        :type regex: Union(str, optional)
        :return: dictionary of all keys with values
        :rtype: dict
        """
        try:
            keys = self._connection.keys(regex)
            values = self._connection.mget(keys)
            keys_with_values = zip_longest(keys, values, fillvalue=None)
        except (ConnectionError, TimeoutError, Exception) as exc:
            raise exc
        return keys_with_values

    def get_all_hash_maps(self, regex='*'):
        """
        return all hash_maps available in the redis.
        .. warning:: It is used only when you know the specific type of keys are hash based keys which are matching regex.

        :param regex - regular expression to check the keys
        :type str
        :returns list of tuples consists of name and dict object
        :rtype list(tuple(str, dict))
        """
        try:
            keys = self._connection.keys(regex)
            pipe = self._connection.pipeline()
            for key in keys:
                pipe.hgetall(key)
            hash_maps_list = pipe.execute()
            keys_with_hash_maps_list = zip_longest(keys, hash_maps_list, fillvalue=None)
            return keys_with_hash_maps_list
        except (ConnectionError, TimeoutError, WatchError, Exception) as exc:
            raise exc

    def hm_set(self, name=None, hash_map=None, namespace=None, delimiter=':'):
        """
        store the python dict object in Redis hash_map format in redis.
        :param name: name of the hash_map
        :type name: str
        :param hash_map: dict object to store
        :type hash_map: dict
        :param namespace: common prefix for set of keys, which uniquely identifies the set of keys among all keys.
        :type namespace: str
        :param delimiter: used in between joining namespace and hash_map name
        :type delimiter: str
        :return: boolean
        :rtype: bool
        :raises Exception
        """
        delimiter = delimiter or ':'
        key = self.get_key_with_or_without_namespace(key=name, namespace=namespace, delimiter=delimiter)
        if not isinstance(hash_map, dict):
            raise Exception('hash_map should be of dict type')
        try:
            res = self._connection.hmset(key, hash_map)
        except (ConnectionError, TimeoutError, Exception) as exc:
            raise exc
        return res

    def h_set(self, name=None, specific_key=None, value=None, namespace=None, delimiter=':'):
        pass

    def h_get(self, name=None, specific_key=None, namespace=None, delimiter=':'):
        """
        get the value of the particular key of hash_map or dict
        :param name: name of the hash_map
        :type name: str
        :param specific_key: specific key to check in hash_map
        :type specific_key: str
        :param namespace: common prefix for set of keys, which uniquely identifies the set of keys among all keys.
        :type namespace: str
        :param delimiter: used in between joining namespace and hash_map name
        :type delimiter: str
        :return: value of the key
        :rtype: Any
        """
        delimiter = delimiter or ':'
        key = self.get_key_with_or_without_namespace(key=name, namespace=namespace, delimiter=delimiter)
        try:
            res = self._connection.hmget(key, specific_key)
        except (ConnectionError, TimeoutError, Exception) as exc:
            raise exc
        return res

    def hm_get(self, name=None, namespace=None, delimiter=None):
        """
        get the dict object stored as hash_map in redis by hash_map name
        :param name: name of the hash_map
        :type name: str
        :param namespace: common prefix for set of keys, which uniquely identifies the set of keys among all keys.
        :type namespace: str
        :param delimiter: used in between joining namespace and hash_map name
        :type delimiter: str
        :return: dict object which is stored as hash_map in redis
        :rtype: dict
        """
        delimiter = delimiter or ':'
        key = self.get_key_with_or_without_namespace(key=name, namespace=namespace, delimiter=delimiter)
        try:
            res = self._connection.hgetall(key)
        except (ConnectionError, TimeoutError, Exception) as exc:
            raise exc
        return res

    @staticmethod
    def get_key_with_or_without_namespace(key=None, namespace=None, delimiter=':'):
        """
        Get the key with namespace has prefix. if no namespace is provided it will return the key
        :param key: name of the key
        :type key: str
        :param namespace: common prefix for set of keys, which uniquely identifies the set of keys among all keys.
        :type namespace: str
        :param delimiter: used in between joining namespace and hash_map name
        :type delimiter: str
        :return: key with or without namespace
        :rtype:
        """
        delimiter = delimiter or ':'
        key_with_or_without_namespace = [x for x in [namespace, key] if x]
        key = delimiter.join(key_with_or_without_namespace)
        return key
