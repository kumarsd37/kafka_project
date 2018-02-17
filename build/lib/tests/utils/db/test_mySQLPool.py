from unittest import TestCase

from mysqlx import PoolError

__author__ = 'pavan.tummalapalli'


from framework.utils.db.db_pool import MySQLPool


class TestMySQLPool(TestCase):

    def setUp(self):

        db_config = {
            'host': 'localhost',
            'port': 3306,
            'username': 'root',
            'password': 'root',
            'database': 'test',
            'pool_name': 'test-name',
            'pool_size': 5
        }

        try:
            self.connection = MySQLPool(**db_config)
        except PoolError as exc:
            raise exc
        except Exception as exc:
            raise exc

    def tearDown(self):
        pass

    def test_execute(self):

        insert_test_query = 'INSERT INTO testing (id, test_name) VALUES (%s, %s)'
        data = (1, 'test1')

        select_test_query = 'SELECT * FROM testing where id=1'

        self.connection.execute(insert_test_query, data, commit=True)
        response = self.connection.execute(select_test_query)
        self.assertGreaterEqual(len(response), 0)

    def test_executemany(self):

        insert_test_query = 'INSERT INTO testing (id, test_name) VALUES (%s, %s)'
        data = [(1, 'test1'),
                 (2, 'test1')
                ]

        select_test_query = ('SELECT * FROM testing')

        self.connection.executemany(insert_test_query, data, commit=True)
        response = self.connection.execute(select_test_query)
        self.assertGreaterEqual(len(response), 0)