import pytest
from unittest.mock import MagicMock, patch
from database import PostgresDb, SqliteDb, get_db  # type: ignore


class MockConfigs:
    def __init__(
        self, dbtype, dbname="test.db", user=None, password=None, host=None, port=None
    ):
        self.dbtype = dbtype
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port


@pytest.fixture
def mock_postgres_configs():
    return MockConfigs(
        dbtype="postgres",
        dbname="test_db",
        user="test_user",
        password="test_pass",
        host="localhost",
        port=5432,
    )


@pytest.fixture
def mock_sqlite_configs():
    return MockConfigs(dbtype="sqlite", dbname=":memory:")


def test_get_db_postgres(mock_postgres_configs):
    db = get_db(mock_postgres_configs)
    assert isinstance(db, PostgresDb)


def test_get_db_sqlite(mock_sqlite_configs):
    db = get_db(mock_sqlite_configs)
    assert isinstance(db, SqliteDb)


def test_get_db_invalid_type():
    configs = MockConfigs(dbtype="invalid")
    with pytest.raises(ValueError, match="Unsupported database type: invalid"):
        get_db(configs)


@patch("database.psycopg2.connect")
def test_postgresdb_connect(mock_connect, mock_postgres_configs):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    db = PostgresDb(mock_postgres_configs)

    with db.connect() as cursor:
        assert cursor == mock_cursor

    mock_cursor.close.assert_called_once()
    mock_connect.return_value.commit.assert_called_once()
    mock_connect.return_value.close.assert_called_once()


@patch("database.sqlite3.connect")
def test_sqlitedb_connect(mock_connect, mock_sqlite_configs):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    db = SqliteDb(mock_sqlite_configs)

    with db.connect() as cursor:
        assert cursor == mock_cursor

    mock_cursor.close.assert_called_once()
    mock_connect.return_value.commit.assert_called_once()
    mock_connect.return_value.close.assert_called_once()


def test_postgresdb_create_schema(mock_postgres_configs):
    db = PostgresDb(mock_postgres_configs)
    db.cursor = MagicMock()
    db.create_schema("test_schema")
    db.cursor.execute.assert_called_once_with(
        "DROP SCHEMA IF EXISTS test_schema CASCADE; CREATE SCHEMA test_schema;"
    )


def test_postgresdb_create_table(mock_postgres_configs):
    db = PostgresDb(mock_postgres_configs)
    db.cursor = MagicMock()
    db.create_table("test_schema", "test_table", ["col1", "col2"])
    db.cursor.execute.assert_called_once_with(
        "DROP TABLE IF EXISTS test_schema.test_table; CREATE TABLE test_schema.test_table (col1 varchar, col2 varchar);"
    )


def test_postgresdb_add_row(mock_postgres_configs):
    db = PostgresDb(mock_postgres_configs)
    db.cursor = MagicMock()
    db.add_row("test_schema", "test_table", ["val1", "val2"])
    db.cursor.execute.assert_called_once_with(
        "INSERT INTO test_schema.test_table VALUES ('val1', 'val2');"
    )


def test_sqlitedb_create_table(mock_sqlite_configs):
    db = SqliteDb(mock_sqlite_configs)
    db.cursor = MagicMock()
    db.create_table(None, "test_table", ["col1", "col2"])
    db.cursor.executescript.assert_called_once_with(
        "DROP TABLE IF EXISTS test_table; CREATE TABLE test_table (col1 TEXT, col2 TEXT);"
    )


def test_sqlitedb_add_row(mock_sqlite_configs):
    db = SqliteDb(mock_sqlite_configs)
    db.cursor = MagicMock()
    db.add_row(None, "test_table", ["val1", "val2"])
    db.cursor.executescript.assert_called_once_with(
        "INSERT INTO test_table VALUES ('val1', 'val2');"
    )
