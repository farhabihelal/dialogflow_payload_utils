import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from datetime import datetime

from csv_exporter import CSVExporter
from do.base_datarow import DataRow

import pandas as pd


class CSVExporterXL(CSVExporter):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

    def dump(self, lines=None, filename=None):

        agent, ext = os.path.splitext(
            os.path.basename(self._config.get("credential", "default-agent.json"))
        )
        datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = (
            filename
            if bool(filename)
            else self._config.get("export_filename")
            if bool(self._config.get("export_filename"))
            else f"{agent}_{datetime_str}.xlsx"
        )
        dir = (
            self._config.get("export_directory")
            if bool(self._config.get("export_directory"))
            else self.default_export_dir
        )
        os.makedirs(dir, exist_ok=True)
        filepath = os.path.join(dir, filename)

        sheets = self.get_sheets(self.rows)
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
        return name.replace("topic-", "").replace("-", " ").title().strip()


if __name__ == "__main__":

    title = "csv exporter dfs"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    import argparse

    default_config = {
        "project_id": "",
        "credential": "",
        "export_directory": "",
        "export_filename": "",
    }

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--project_id",
        dest="project_id",
        type=str,
        default=default_config.get("project_id", ""),
        help="Google Cloud Project Id",
    )
    parser.add_argument(
        "--credential",
        dest="credential",
        type=str,
        default=default_config.get("credential", ""),
        help="Path to Google Cloud Project credential",
    )
    parser.add_argument(
        "--export_directory",
        dest="export_directory",
        type=str,
        default=default_config.get("export_directory", ""),
        help="Absolute path to export directory",
    )
    parser.add_argument(
        "--export_filename",
        dest="export_filename",
        type=str,
        default=default_config.get("export_filename", ""),
        help="Name of the exported file",
    )

    args, args_list = parser.parse_known_args()

    config = {
        "project_id": args.project_id,
        "credential": args.credential,
        "export_directory": args.export_directory,
        "export_filename": args.export_filename,
    }

    exporter = CSVExporterXL(config)
    exporter.run()
