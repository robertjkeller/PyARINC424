from pyarinc424.arinc import ArincParser
from pyarinc424.config import UserConfigs
from pyarinc424.database import DbConfig, get_db
import sys


def main() -> None:
    if len(sys.argv) > 1:
        kwargs = {"config_file": sys.argv[1]}
    else:
        kwargs = {}

    configs: UserConfigs = UserConfigs(**kwargs)

    db: DbConfig = get_db(configs)

    with db.connect():
        parser = ArincParser(db, configs.file_loc)
        parser.parse()


if __name__ == "__main__":  # pragma: no cover
    main()
