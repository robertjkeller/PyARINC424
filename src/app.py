from rich.progress import track
from database import PostgresDb
from config import UserConfigs
from record_maps import record_maps


configs = UserConfigs()


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


class ArincParser:
    '''
    Parser that iterates through record mappings, extracts each record's
    data from the main ARINC-format file, and adds the data to the 
    PostgreSQL database.
    '''
    def __init__(self, cursor, file=configs.file_loc):
        self.cursor = cursor
        self.file = file
        self.lines = self.read_file()
        self.cycle = self.get_cycle()

    def read_file(self) -> str:
        '''Reads the CIFP/ARINC-424 formatted file.'''
        with open(self.file) as file:
            return file.readlines()

    def parse(self) -> None:
        self.create_schema()
        for record in record_maps:
            self.create_arinc_record(record)

    def get_cycle(self) -> str:
        '''Gets the file's AIRAC cycle for schema naming.'''
        return self.lines[0][35:39]

    def create_schema(self) -> None:
        '''Creates database schema for the given cycle. Drops existing schema.'''
        sql = f"DROP SCHEMA IF EXISTS cycle{self.cycle} CASCADE; CREATE SCHEMA cycle{self.cycle};"
        self.cursor.execute(sql)

    def create_table(self, record: ArincRecord, cycle: str) -> None:
        '''Creates a table in the PostgreSQL database for an ARINC record.'''
        sql = f"""
               DROP TABLE IF EXISTS cycle{cycle}.{record.name}; 
               CREATE TABLE cycle{cycle}.{record.name} 
               ({' varchar, '.join([c for c in record.column_names])} varchar);
               """
        self.cursor.execute(sql)

    def add_row(self, name: str, values: list, cycle: str) -> None:
        '''Adds a row to its ARINC record PostgreSQL table.'''
        values = [v.replace("'", "''") for v in values]
        values_joined = ", ".join([f"'{v.rstrip()}'" for v in values])
        sql = f"INSERT INTO cycle{cycle}.{name} VALUES ({values_joined});"
        self.cursor.execute(sql)

    def create_arinc_record(self, record_map) -> None:
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
    with PostgresDb(configs).connect() as cursor:
        parser = ArincParser(cursor)
        parser.parse()


if __name__ == "__main__":
    main()
