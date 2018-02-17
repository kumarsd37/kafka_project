from mysql.connector import ProgrammingError
from mysqlx import PoolError

__author__ = 'pavan.tummalapalli'


import mysql.connector.pooling
import logging


logger = logging.getLogger(__name__)


class MySQLPool:
    """
    create a pool, when connect to mysql, which will decrease the time spent in
    request connection, create connection and close connection.
    """
    def __init__(self, **db):
        res = dict()
        self._host = db.get('host')
        self._port = db.get('port')
        self._user = db.get('username')
        self._password = db.get('password')
        self._database = db.get('database')

        res["host"] = self._host
        res["port"] = self._port
        res["user"] = self._user
        res["password"] = self._password
        res["database"] = self._database
        self.dbconfig = res
        self.pool = self.create_pool(pool_name=db.get('pool_name'), pool_size=db.get('pool_size'))

    def create_pool(self, pool_name='default', pool_size=3):
        """
        Create a connection pool, after created, the request of connecting
        MySQL could get a connection from this pool instead of request to
        create a connection.

        :param pool_name: the name of pool, default is "default"
        :param pool_size: the size of pool, default is 3
        :return: connection pool
        """
        try:
            pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                pool_reset_session=True,
                **self.dbconfig)
        except PoolError as exc:
            # logger.exception calls error(message, exc_info=1) internally
            logger.exception(exc.__str__())
            raise exc
        except Exception as exc:
            logger.exception(exc.__str__())
            raise exc
        return pool

    def close(self, conn, cursor):
        """
        A method used to close connection of mysql.
        :param conn: connection object
        :param cursor: cursor object
        :return: None
        """
        cursor.close()
        conn.close()

    def execute(self, sql, args=None, commit=False):
        """
        Execute a sql, it could be with args and with out args. The usage is
        similar with execute() function in module pymysql.

        Insert example:
        ::

            tomorrow = datetime.now().date() + timedelta(days=1)

            add_employee = ("INSERT INTO employees "
               "(first_name, last_name, hire_date, gender, birth_date) "
               "VALUES (%s, %s, %s, %s, %s)")

            add_salary = ("INSERT INTO salaries "
              "(emp_no, salary, from_date, to_date) "
              "VALUES (%(emp_no)s, %(salary)s, %(from_date)s, %(to_date)s)")

            data_employee = ('Geert', 'Vanderkelen', tomorrow, 'M', date(1977, 6, 14))
            execute(add_employee, data_employee)

        :param sql: sql clause
        :param args: args need by sql clause
        :param commit: whether to commit
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, args)
        except ProgrammingError as exc:
            raise exc
        except Exception as exc:
            raise exc
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return None
        else:
            try:
                res = cursor.fetchall()
            except Exception as exc:
                logger.exception(exc.__str__())
                res = None
            finally:
                self.close(conn, cursor)
            return res

    def executemany(self, sql, args, commit=False):
        """
        Example of mysql executemany insert:
        ::
            sqlquery = ("INSERT INTO employees "
               "(first_name, last_name, hire_date, gender, birth_date) "
               "VALUES (%s, %s, %s, %s, %s)")

            data = [
                  ('Jane', date(2005, 2, 12)),
                  ('Joe', date(2006, 5, 23)),
                  ('John', date(2010, 10, 3)),
                ]

                obj.executemany(sqlquery, data)

        Execute with many args. Similar with executemany() function in pymysql.
        args should be a sequence.
        :param sql: sql clause
        :param args: args
        :param commit: commit or not.
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, args)
        except ProgrammingError as exc:
            raise exc
        except Exception as exc:
            raise exc
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return None
        else:
            res = cursor.fetchall()
            self.close(conn, cursor)
            return res
