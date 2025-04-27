from rich.progress import track
from database import get_db 
from config import UserConfigs
from record_maps import record_maps


configs = UserConfigs()


class ArincRecord:
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
    def __init__(self, db, file=configs.file_loc):
        self.db = db
        self.file = file
        self.lines = self.read_file()
        self.cycle = self.get_cycle()
        self.schema = f"cycle{self.cycle}"

    def read_file(self) -> str:
        with open(self.file) as file:
            return file.readlines()

    def parse(self) -> None:
        self.create_schema()
        for record in record_maps:
            self.create_arinc_record(record)

    def get_cycle(self) -> str:
        return self.lines[0][35:39]

    def create_schema(self) -> None:
        self.db.create_schema(self.schema)

    def create_table(self, record: ArincRecord, cycle: str) -> None:
        self.db.create_table(self.schema, record.name, record.column_names)
        
    def add_row(self, name: str, values: list, cycle: str) -> None:
        self.db.add_row(self.schema, name, values)
        
    def create_arinc_record(self, record_map) -> None:
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
    db = get_db(configs)

    with db.connect():
        parser = ArincParser(db)
        parser.parse()


if __name__ == "__main__":
    main()
