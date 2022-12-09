import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from csv_exporter_xl import CSVExporterXL
from do.base_datarow import DataRow

import pandas as pd


class ESExporter(CSVExporterXL):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

    def get_sheets(self, rows: list):
        sheets = super().get_sheets(rows)
        return self.get_demo_sheets(sheets)

    def get_demo_sheets(self, sheets=None):

        demo_data = self._config["demo_data"]

        demo_sheets = {}

        for day in demo_data:
            for session in demo_data[day]:
                sheet_name = f"day-{day}-session-{session}"
                if not demo_sheets.get(sheet_name):
                    demo_sheets[sheet_name] = []

                for intent_name in demo_data[day][session]:
                    intents = sheets[self.process_sheet_name(intent_name)]
                    demo_sheets[sheet_name].extend(intents)

        return demo_sheets


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

    # config = {
    #     "project_id": args.project_id,
    #     "credential": args.credential,
    #     "export_directory": args.export_directory,
    #     "export_filename": args.export_filename,
    #     "algorithm": "dfs",
    # }

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/..")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    demo_data = {
        "1": {
            "1": [
                "topic-names-origins",
                "topic-age",
            ],
            "2": [
                "topic-hometown",
                "topic-travel-homecountry",
            ],
        },
    }

    config = {
        "project_id": "empathetic-stimulator-owp9",
        "credential": os.path.abspath(os.path.join(agents_dir, "es.json")),
        "export_directory": exports_dir,
        "export_filename": "ES.xlsx",
        "algorithm": "dfs",
        "mode": "text",
        "demo_data": demo_data,
    }

    exporter = ESExporter(config)
    exporter.run()
