import pytest
from unittest import mock
import configparser
from config import UserConfigs, validate  # type: ignore


class TestValidate:
    def test_valid_postgres_config(self):
        """Test validation with valid PostgreSQL configuration."""
        parser = configparser.ConfigParser()
        parser["postgres"] = {
            "dbname": "testdb",
            "user": "testuser",
            "password": "testpass",
            "host": "localhost",
            "port": "5432",
        }
        parser["cifp_file"] = {"file_loc": "/path/to/file"}

        # Should not raise any exceptions
        validate(parser)

    def test_valid_sqlite_config(self):
        """Test validation with valid SQLite configuration."""
        parser = configparser.ConfigParser()
        parser["sqlite"] = {"dbname": "test.db"}
        parser["cifp_file"] = {"file_loc": "/path/to/file"}

        # Should not raise any exceptions
        validate(parser)

    def test_no_database_config(self):
        """Test validation fails when no database configuration is provided."""
        parser = configparser.ConfigParser()
        parser["cifp_file"] = {"file_loc": "/path/to/file"}

        with pytest.raises(ValueError, match="No database configuration found"):
            validate(parser)

    def test_multiple_database_configs(self):
        """Test validation fails when multiple database configurations are provided."""
        parser = configparser.ConfigParser()
        parser["postgres"] = {
            "dbname": "testdb",
            "user": "testuser",
            "password": "testpass",
            "host": "localhost",
            "port": "5432",
        }
        parser["sqlite"] = {"dbname": "test.db"}
        parser["cifp_file"] = {"file_loc": "/path/to/file"}

        with pytest.raises(ValueError, match="Only one database configuration allowed"):
            validate(parser)

    def test_missing_postgres_keys(self):
        """Test validation fails when required PostgreSQL keys are missing."""
        parser = configparser.ConfigParser()
        parser["postgres"] = {
            "dbname": "testdb",
            "user": "testuser",
            # Missing password, host, port
        }
        parser["cifp_file"] = {"file_loc": "/path/to/file"}

        with pytest.raises(
            ValueError, match="Missing required PostgreSQL configuration"
        ):
            validate(parser)

    def test_missing_sqlite_key(self):
        """Test validation fails when required SQLite key is missing."""
        parser = configparser.ConfigParser()
        parser["sqlite"] = {}  # Missing dbname
        parser["cifp_file"] = {"file_loc": "/path/to/file"}

        with pytest.raises(ValueError, match="Missing required SQLite configuration"):
            validate(parser)

    def test_missing_cifp_file_section(self):
        """Test validation fails when cifp_file section is missing."""
        parser = configparser.ConfigParser()
        parser["postgres"] = {
            "dbname": "testdb",
            "user": "testuser",
            "password": "testpass",
            "host": "localhost",
            "port": "5432",
        }

        with pytest.raises(
            ValueError, match="Missing required cifp_file configuration"
        ):
            validate(parser)

    def test_missing_file_loc(self):
        """Test validation fails when file_loc option is missing."""
        parser = configparser.ConfigParser()
        parser["postgres"] = {
            "dbname": "testdb",
            "user": "testuser",
            "password": "testpass",
            "host": "localhost",
            "port": "5432",
        }
        parser["cifp_file"] = {}  # Missing file_loc

        with pytest.raises(ValueError, match="File location cannot be empty"):
            validate(parser)


class TestUserConfigs:
    @mock.patch("configparser.ConfigParser.read")
    def test_postgres_config(self, mock_read):
        """Test UserConfigs initialization with PostgreSQL configuration."""
        mock_config = configparser.ConfigParser()
        mock_config["postgres"] = {
            "dbname": "testdb",
            "user": "testuser",
            "password": "testpass",
            "host": "localhost",
            "port": "5432",
        }
        mock_config["cifp_file"] = {"file_loc": "/path/to/file"}

        # Setup the mock to return our config
        with mock.patch("configparser.ConfigParser", return_value=mock_config):
            # Should not raise any exceptions
            user_configs = UserConfigs()

            # Check that attributes were set correctly
            assert user_configs.dbtype == "postgres"
            assert user_configs.dbname == "testdb"
            assert user_configs.user == "testuser"
            assert user_configs.password == "testpass"
            assert user_configs.host == "localhost"
            assert user_configs.port == "5432"
            assert user_configs.file_loc == "/path/to/file"

    @mock.patch("configparser.ConfigParser.read")
    def test_sqlite_config(self, mock_read):
        """Test UserConfigs initialization with SQLite configuration."""
        mock_config = configparser.ConfigParser()
        mock_config["sqlite"] = {"dbname": "test.db"}
        mock_config["cifp_file"] = {"file_loc": "/path/to/file"}

        # Setup the mock to return our config
        with mock.patch("configparser.ConfigParser", return_value=mock_config):
            # Should not raise any exceptions
            user_configs = UserConfigs()

            # Check that attributes were set correctly
            assert user_configs.dbtype == "sqlite"
            assert user_configs.dbname == "test.db"
            assert user_configs.file_loc == "/path/to/file"

    @mock.patch("configparser.ConfigParser.read")
    def test_missing_config(self, mock_read):
        """Test UserConfigs initialization fails with missing configuration."""
        mock_config = configparser.ConfigParser()

        # Setup the mock to return an empty config
        with mock.patch("configparser.ConfigParser", return_value=mock_config):
            with pytest.raises(ValueError, match="No database configuration found"):
                UserConfigs()

    @mock.patch("configparser.ConfigParser.read")
    def test_invalid_config(self, mock_read):
        """Test UserConfigs initialization fails with invalid configuration."""
        mock_config = configparser.ConfigParser()
        mock_config["postgres"] = {"dbname": "testdb"}  # Missing required keys
        mock_config["cifp_file"] = {"file_loc": "/path/to/file"}

        # Setup the mock to return an invalid config
        with mock.patch("configparser.ConfigParser", return_value=mock_config):
            with pytest.raises(
                ValueError, match="Missing required PostgreSQL configuration"
            ):
                UserConfigs()
