from contextlib import contextmanager
import psycopg2


class PostgresDb:
    def __init__(self, configs):
        self.params = {
            'dbname': configs.dbname,
            'user':  configs.user,
            'password': configs.password,
            'host': configs.host,
            'port': configs.port
        }

    @contextmanager
    def connect(self):
        conn = psycopg2.connect(**self.params)
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
            conn.commit()
            conn.close()
