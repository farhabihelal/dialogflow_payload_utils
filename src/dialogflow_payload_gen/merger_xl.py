import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from parser_xl import ParserXL
from exporter_xl import ExporterXL

from do.base_datarow import DataRow

from datetime import datetime

import pandas as pd


class MergerXL:
    def __init__(self, config: dict) -> None:
        self.configure(config)

        self._src_data = None
        self._src_data_rr = None

        self._dst_data = None
        self._dst_data_rr = None

        self._src_datamap = None
        self._dst_datamap = None

    def configure(self, config: dict):
        self.config = config

    def merge(self):
        pass

    def merge_data(self, src_data: list, dst_data: list):
        merged_data = []

        for src_datarow in src_data:
            src_datarow: DataRow

            merged_datarow = src_datarow

            try:
                idx = dst_data.index(src_datarow)
                dst_datarow: DataRow = dst_data[idx]
                merged_datarow = dst_datarow

                if dst_datarow.genre != src_datarow.genre:
                    merged_datarow.genre = src_datarow.genre

                if dst_datarow.routine != src_datarow.routine:
                    merged_datarow.routine = src_datarow.routine

                if dst_datarow.routine_id != src_datarow.routine_id:
                    merged_datarow.routine_id = src_datarow.routine_id

            except ValueError as e:
                pass

            merged_data.append(merged_datarow)

        return merged_data

    def load_data(self, filepath: str):
        parser = ParserXL({"filepath": filepath})
        parser.run()

        data = [parser.get_datarow(x) for x in parser._data]

        return data

    def dump(self, rows=None, filename=None):
        rows = rows if rows else self.rows

        datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = filename if filename else self.config.get("export_filename")
        dir = (
            os.path.join(self.config.get("export_directory"), datetime_str)
            if self.config.get("export_directory")
            else os.path.join(os.getcwd(), "merger_exports", datetime_str)
        )
        os.makedirs(dir, exist_ok=True)
        filepath = os.path.join(dir, filename)

        sheets = self.get_sheets(rows)
        self.create_xlsx(sheets, filepath)

    def get_sheets(self, rows: list):
        sheets = {}

        for row in rows:
            row: DataRow
            sheet_name = self.process_sheet_name(row.topic)
            if not sheets.get(sheet_name):
                sheets[sheet_name] = []

            sheets[sheet_name].append(row.tolist())

        return {k: sheets[k] for k in sorted(sheets.keys())}

    def create_xlsx(self, sheets: dict, filepath: str = None):
        writer = pd.ExcelWriter(filepath)

        for sheet_name in sheets:
            df = pd.DataFrame(sheets[sheet_name], columns=DataRow.all_fields())
            df.to_excel(
                excel_writer=writer,
                sheet_name=sheet_name,
                index=False,
            )

        writer.save()

    def process_sheet_name(self, name: str):
        return name.replace("topic-", "").replace(" ", "-").lower().strip()

    def run(self, src_filepath: str = None, dst_filepath: str = None):
        src_filepath = src_filepath if src_filepath else self.config["src_filepath"]
        dst_filepath = dst_filepath if dst_filepath else self.config["dst_filepath"]

        src_data = self.load_data(src_filepath)
        dst_data = self.load_data(dst_filepath)

        self._src_data = src_data
        self._dst_data = dst_data

        merged_data = self.merge_data(src_data, dst_data)

        self.dump(rows=merged_data)


if __name__ == "__main__":
    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    config = {
        "src_filepath": os.path.join(exports_dir, "ES_GS.xlsx"),
        "dst_filepath": os.path.join(exports_dir, "ES_v3.xlsx"),
        "export_directory": os.path.join(exports_dir, "mergers"),
        "export_filename": "ES_Merged.xlsx",
    }

    merger = MergerXL(config)
    merger.run()
