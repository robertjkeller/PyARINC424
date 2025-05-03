import configparser


class UserConfigs:
    def __init__(self, config_file: str = "config.ini"):
        parser = configparser.ConfigParser()
        read = parser.read(config_file)

        if not read:
            raise FileNotFoundError(f"Configuration file {config_file} not found")

        validate(parser)

        if parser.has_section("postgres"):
            self.dbtype = "postgres"
            self.dbname = parser["postgres"]["dbname"]
            self.user = parser["postgres"]["user"]
            self.password = parser["postgres"]["password"]
            self.host = parser["postgres"]["host"]
            self.port = parser["postgres"]["port"]

        if parser.has_section("sqlite"):
            self.dbtype = "sqlite"
            self.dbname = parser["sqlite"]["dbname"]

        self.file_loc = parser["cifp_file"]["file_loc"]


def validate(parser: configparser.ConfigParser) -> None:
    if not parser.has_section("postgres") and not parser.has_section("sqlite"):
        raise ValueError("No database configuration found in config.ini")

    if parser.has_section("postgres") and parser.has_section("sqlite"):
        raise ValueError("Only one database configuration allowed in config.ini")

    if parser.has_section("postgres"):
        if not all(
            key in parser["postgres"]
            for key in ["dbname", "user", "password", "host", "port"]
        ):
            raise ValueError("Missing required PostgreSQL configuration keys")

    if parser.has_section("sqlite"):
        if "dbname" not in parser["sqlite"]:
            raise ValueError("Missing required SQLite configuration key: dbname")

    if not parser.has_section("cifp_file"):
        raise ValueError("Missing required cifp_file configuration key: file_loc")

    if not parser.has_option("cifp_file", "file_loc"):
        raise ValueError("File location cannot be empty")
