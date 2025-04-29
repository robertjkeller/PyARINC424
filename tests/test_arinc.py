import os
import tempfile

import arinc  # type: ignore


class MockDbConfig:
    def __init__(self):
        self.schemas_created = []
        self.tables_created = []
        self.rows_added = []

    def create_schema(self, schema_name: str) -> None:
        self.schemas_created.append(schema_name)

    def create_table(
        self, schema_name: str, table_name: str, columns: list[str]
    ) -> None:
        self.tables_created.append((schema_name, table_name, columns))

    def add_row(self, schema_name: str, table_name: str, values: list[str]) -> None:
        self.rows_added.append((schema_name, table_name, values))


def test_arinc_parser_parse():
    test_record_map = {
        "section_code": "A",
        "subsection_code": "B",
        "section_pos": 0,
        "subsection_pos": 1,
        "cont_rec_pos": 2,
        "cont_rec_vals": ["C"],
        "name": "test_record_parser",
        "columns": [
            {"name": "col1", "start": 3, "end": 5},
            {"name": "col2", "start": 5, "end": 7},
        ],
    }
    arinc.record_maps = [test_record_map]

    cycle_line = "X" * 35 + "2023\n"
    line_match = "ABCDEFAB\n"
    line_nomatch = "ZZZZZZZZ\n"
    file_content = cycle_line + line_match + line_nomatch + line_match

    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_file:
        tmp_file.write(file_content)
        tmp_file_path = tmp_file.name

    try:
        mock_db = MockDbConfig()
        parser = arinc.ArincParser(mock_db, tmp_file_path)
        parser.parse()

        expected_schema = "cycle2023"
        assert expected_schema in mock_db.schemas_created

        expected_table = (expected_schema, "test_record_parser", ["col1", "col2"])
        assert expected_table in mock_db.tables_created

        expected_row = ["DE", "FA"]
        matching_rows = [
            row for _, tbl, row in mock_db.rows_added if tbl == "test_record_parser"
        ]
        assert len(matching_rows) == 2
        for row in matching_rows:
            assert row == expected_row
    finally:
        os.unlink(tmp_file_path)


def test_arinc_record():
    record_map = {
        "section_code": 1,
        "subsection_code": 2,
        "section_pos": 3,
        "subsection_pos": 4,
        "cont_rec_pos": 5,
        "cont_rec_vals": ["val1", "val2"],
        "name": "test_record",
        "columns": [{"name": "col1"}, {"name": "col2"}],
    }
    record = arinc.ArincRecord(record_map)

    assert record.section == 1
    assert record.subsection == 2
    assert record.section_pos == 3
    assert record.subsection_pos == 4
    assert record.cont_rec_pos == 5
    assert record.cont_rec_vals == ["val1", "val2"]
    assert record.name == "test_record"
    assert record.column_names == ["col1", "col2"]
