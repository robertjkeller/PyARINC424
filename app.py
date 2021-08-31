from rich.progress import track
from record_info import record_map
import configparser
import psycopg2


class Configs:
    def __init__(self, config_file="config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.file = config["cifp_file"]["file_loc"]

        self.dbname = config["postgres"]["dbname"]
        self.user = config["postgres"]["user"]
        self.password = config["postgres"]["password"]
        self.host = config["postgres"]["host"]
        self.port = config["postgres"]["port"]


class PgConn:
    def __init__(self, configs: Configs):
        config = configparser.ConfigParser()
        config.read("config.ini")

        self.conn = psycopg2.connect(
            dbname=configs.dbname,
            user=configs.user,
            password=configs.password,
            host=configs.host,
            port=configs.port,
        )

        self.cur = self.conn.cursor()

    def commit_and_close(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create_schema(self, cycle: str) -> None:
        sql = f"DROP SCHEMA IF EXISTS cycle{cycle} CASCADE; CREATE SCHEMA cycle{cycle};"
        self.cur.execute(sql)

    def create_table(self, name: str, columns: list, cycle: str) -> None:
        sql = f"""DROP TABLE IF EXISTS cycle{cycle}.{name}; 
                CREATE TABLE cycle{cycle}.{name} ({' varchar, '.join([c for c in columns])} varchar);"""
        self.cur.execute(sql)

    def add_row(self, name: str, values: list, cycle: str) -> None:
        values = [v.replace("'", "''") for v in values]
        values_joined = ", ".join([f"'{v}'" for v in values])
        sql = f"INSERT INTO cycle{cycle}.{name} VALUES ({values_joined});"

        self.cur.execute(sql)


class ArincParser:
    def __init__(self, configs: Configs, conn: PgConn):

        with open(configs.file) as file:
            self.lines = file.readlines()

        self.cycle = self.lines[0][35:39]

        self.conn = conn

    def parse(self):
        self.conn.create_schema(self.cycle)

        for record in record_map:

            record_name = record.get("name")
            columns = [c["name"] for c in record["columns"]]

            self.conn.create_table(record_name, columns, self.cycle)

            section = record.get("section_code")
            subsection = record.get("subsection_code")
            section_pos = record.get("section_pos")
            subsection_pos = record.get("subsection_pos")
            cont_rec_pos = record.get("cont_rec_pos")
            cont_rec_val = str(record.get("cont_rec_val"))

            for line in track(self.lines, description=f"{record_name.rjust(23)}"):
                if (
                    line[section_pos] == section
                    and line[subsection_pos] == subsection
                    and line[cont_rec_pos] == cont_rec_val
                ):
                    row = [f"{line[i['start']:i['end']]}" for i in record["columns"]]
                    self.conn.add_row(record_name, row, self.cycle)


def main():
    configs = Configs()
    pg_conn = PgConn(configs)
    parser = ArincParser(configs, pg_conn)

    parser.parse()

    pg_conn.commit_and_close()


if __name__ == "__main__":
    main()
