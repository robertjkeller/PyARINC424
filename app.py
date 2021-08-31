from rich.progress import track
from record_maps import record_maps
import configparser
import psycopg2


class Configs:
    def __init__(self, config_file="config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.dbname = config["postgres"]["dbname"]
        self.user = config["postgres"]["user"]
        self.password = config["postgres"]["password"]
        self.host = config["postgres"]["host"]
        self.port = config["postgres"]["port"]
        self.file = config["cifp_file"]["file_loc"]


class PgConn(Configs):
    def connect(self):

        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
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


class ArincParser(PgConn):
    def parse(self):    # function sould probably be renamed.
        self.connect()

        self.cycle = self.get_cycle()
        self.create_schema(self.cycle)

    def create_arinc_record(self, record_map):
        record = ArincRecord(record_map)

        self.create_table(record.name, record.column_names, self.cycle)

        for line in track(self.lines, description=f"{record.name.rjust(23)}"):
            if (
                line[record.section_pos] == record.section
                and line[record.subsection_pos] == record.subsection
                and line[record.cont_rec_pos] == record.cont_rec_val
            ):
                row = [f"{line[i['start']:i['end']]}" for i in record.columns]
                self.add_row(record.name, row, self.cycle)

    def get_cycle(self):
        with open(self.file) as file:
            self.lines = file.readlines()
        cycle = self.lines[0][35:39]
        return cycle


class ArincRecord:
    def __init__(self, record_map: dict):
        self.section = record_map.get("section_code")
        self.subsection = record_map.get("subsection_code")
        self.section_pos = record_map.get("section_pos")
        self.subsection_pos = record_map.get("subsection_pos")
        self.cont_rec_pos = record_map.get("cont_rec_pos")
        self.cont_rec_val = str(record_map.get("cont_rec_val"))

        self.name = record_map.get("name")
        self.columns = record_map.get("columns")
        self.column_names = [c["name"] for c in record_map["columns"]]


def main():
    parser = ArincParser()

    parser.parse()

    for record in record_maps:
        parser.create_arinc_record(record)

    parser.commit_and_close()


if __name__ == "__main__":
    main()
