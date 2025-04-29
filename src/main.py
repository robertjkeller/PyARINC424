from arinc import ArincParser
from config import UserConfigs
from database import DbConfig, get_db


def main() -> None:
    configs: UserConfigs = UserConfigs()

    db: DbConfig = get_db(configs)

    with db.connect():
        parser = ArincParser(db, configs.file_loc)
        parser.parse()


if __name__ == "__main__":  # pragma: no cover
    main()
