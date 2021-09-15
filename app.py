from rich.progress import track
from record_maps import record_maps
import configparser
import psycopg2


class ArincRecord:
    '''Represents an ARINC-424 format file record.'''
    def __init__(self, record_map: dict):
        self.section = record_map.get("section_code")
        self.subsection = record_map.get("subsection_code")
        self.section_pos = record_map.get("section_pos")
        self.subsection_pos = record_map.get("subsection_pos")
        self.cont_rec_pos = record_map.get("cont_rec_pos")
        self.cont_rec_vals = record_map.get("cont_rec_vals")
        self.name = record_map.get("name")
        self.columns = record_map.get("columns")
        self.column_names = [c["name"] for c in record_map["columns"]]


class Configs:
    '''User config settings from config file.'''
    def __init__(self, config_file="config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.dbname = config["postgres"]["dbname"]
        self.user = config["postgres"]["user"]
        self.password = config["postgres"]["password"]
        self.host = config["postgres"]["host"]
        self.port = config["postgres"]["port"]
        self.file = config["cifp_file"]["file_loc"]


class ArincParser(Configs):
    '''
    Parser that iterates through record mappings, extracts each record's
    data from the main ARINC-format file, and adds the data to the 
    PostgreSQL database.
    '''
    def __init__(self):
        super().__init__()
        self.connect()
        self.lines = self.read_file()
        self.cycle = self.get_cycle()

    def connect(self):
        '''Establishes connection to PostgreSQL database.'''
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.cur = self.conn.cursor()

    def read_file(self):
        '''Reads the CIFP/ARINC-424 formatted file.'''
        with open(self.file) as file:
            return file.readlines()

    def get_cycle(self):
        '''Gets the file's AIRAC cycle for schema naming.'''
        return self.lines[0][35:39]

    def commit_and_close(self):
        '''Commits changes and closes PostgreSQL connection.'''
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create_schema(self) -> None:
        '''Creates database schema for the given cycle. Drops existing schema.'''
        sql = f"DROP SCHEMA IF EXISTS cycle{self.cycle} CASCADE; CREATE SCHEMA cycle{self.cycle};"
        self.cur.execute(sql)

    def create_table(self, record: ArincRecord, cycle: str) -> None:
        '''Creates a table in the PostgreSQL database for an ARINC record.'''
        sql = f"""DROP TABLE IF EXISTS cycle{cycle}.{record.name}; 
                CREATE TABLE cycle{cycle}.{record.name} 
                ({' varchar, '.join([c for c in record.column_names])} varchar);"""
        self.cur.execute(sql)

    def add_row(self, name: str, values: list, cycle: str) -> None:
        '''Adds a row to its ARINC record PostgreSQL table.'''
        values = [v.replace("'", "''") for v in values]
        values_joined = ", ".join([f"'{v.rstrip()}'" for v in values])
        sql = f"INSERT INTO cycle{cycle}.{name} VALUES ({values_joined});"
        self.cur.execute(sql)

    def create_arinc_record(self, record_map):
        '''
        For a given ARINC record, parse data out of the main file and 
        add it to the record's PostgreSQL database table.
        '''
        record = ArincRecord(record_map)

        self.create_table(record, self.cycle)

        for line in track(self.lines, description=f"{record.name.rjust(26)}"):
            if (
                line[record.section_pos] == record.section
                and line[record.subsection_pos] == record.subsection
            ):
                if (
                    not record.cont_rec_pos
                    or line[record.cont_rec_pos] in record.cont_rec_vals
                ):
                    row = [f"{line[i['start']:i['end']]}" for i in record.columns]
                    self.add_row(record.name, row, self.cycle)


def main():
    parser = ArincParser()

    for record in record_maps:
        parser.create_arinc_record(record)

    parser.commit_and_close()


if __name__ == "__main__":
    main()
