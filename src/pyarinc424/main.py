from .arinc import ArincParser
from .config import UserConfigs
from .database import DbConfig, get_db
import sys


def main() -> None:
    if len(sys.argv) > 1:
        kwargs = {"config_file": sys.argv[1]}

    configs: UserConfigs = UserConfigs(**kwargs)

    db: DbConfig = get_db(configs)

    with db.connect():
        parser = ArincParser(db, configs.file_loc)
        parser.parse()


if __name__ == "__main__":  # pragma: no cover
    main()
