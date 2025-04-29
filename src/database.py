from contextlib import contextmanager
import psycopg2  # type: ignore
import sqlite3
from typing import Protocol, Generator
from config import UserConfigs


class DbConfig(Protocol):  # pragma: no cover
    def connect(self):
        pass

    def create_schema(self, schema_name: str) -> None:
        pass

    def create_table(
        self, schema_name: str, table_name: str, columns: list[str]
    ) -> None:
        pass

    def add_row(self, schema_name: str, table_name: str, values: list[str]) -> None:
        pass


class PostgresDb:
    def __init__(self, configs) -> None:
        self.params = {
            "dbname": configs.dbname,
            "user": configs.user,
            "password": configs.password,
            "host": configs.host,
            "port": configs.port,
        }

        self.schema = ""

    @contextmanager
    def connect(self) -> Generator[psycopg2.extensions.cursor, None, None]:
        conn = psycopg2.connect(**self.params)
        self.cursor = conn.cursor()
        try:
            yield self.cursor
        finally:
            self.cursor.close()
            conn.commit()
            conn.close()

    def create_schema(self, schema_name: str) -> None:
        self.schema = schema_name
        sql = (
            f"DROP SCHEMA IF EXISTS {schema_name} CASCADE; CREATE SCHEMA {schema_name};"
        )
        self.cursor.execute(sql)

    def create_table(
        self, schema_name: str, table_name: str, columns: list[str]
    ) -> None:
        column_defs = ", ".join([f"{col} varchar" for col in columns])
        sql = f"DROP TABLE IF EXISTS {schema_name}.{table_name}; CREATE TABLE {schema_name}.{table_name} ({column_defs});"
        self.cursor.execute(sql)

    def add_row(self, schema_name: str, table_name: str, values: list[str]) -> None:
        values = [v.replace("'", "''") for v in values]
        values_joined = ", ".join([f"'{v.rstrip()}'" for v in values])
        sql = f"INSERT INTO {schema_name}.{table_name} VALUES ({values_joined});"
        self.cursor.execute(sql)


class SqliteDb:
    def __init__(self, configs) -> None:
        self.dbname = configs.dbname
        self.schema = ""

    @contextmanager
    def connect(self) -> Generator[sqlite3.Cursor, None, None]:
        conn = sqlite3.connect(self.dbname)
        self.cursor = conn.cursor()
        try:
            yield self.cursor
        finally:
            self.cursor.close()
            conn.commit()
            conn.close()

    def create_schema(self, _) -> None:  # pragma: no cover
        # SQLite does not support schemas in the same way as PostgreSQL.
        # This method is intentionally a no-op.
        pass

    def create_table(self, _, table_name: str, columns: list[str]) -> None:
        column_defs = ", ".join([f"{col} TEXT" for col in columns])
        sql = f"DROP TABLE IF EXISTS {table_name}; CREATE TABLE {table_name} ({column_defs});"
        self.cursor.executescript(sql)

    def add_row(self, _, table_name: str, values: list[str]) -> None:
        values = [v.replace("'", "''") for v in values]
        values_joined = ", ".join([f"'{v.rstrip()}'" for v in values])
        sql = f"INSERT INTO {table_name} VALUES ({values_joined});"
        self.cursor.executescript(sql)


def get_db(configs: UserConfigs) -> DbConfig:
    if configs.dbtype == "postgres":
        return PostgresDb(configs)
    elif configs.dbtype == "sqlite":
        return SqliteDb(configs)
    else:
        raise ValueError(f"Unsupported database type: {configs.dbtype}")
