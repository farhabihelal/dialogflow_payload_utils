import json

import __init__


from dialogflow_api.src import dialogflow as df

from csv_exporter import CSVExporter
from csv_parser import CSVParser


class RichResponseValidator:
    def __init__(self, config) -> None:
        self.config = config

        self.exporter = CSVExporter(config["exporter"])

        self.parser = CSVParser(config["parser"])

    def run(self):
        self.exporter.run()
        self.parser.run()

        exporter_rr = self.exporter.rich_responses
        parser_rr = self.parser.parsed_data

        print(f"hash of exporter_rr: {hash(json.dumps(exporter_rr))}")
        print(f"hash of parser_rr: {hash(json.dumps(parser_rr))}")


if __name__ == "__main__":

    title = "rich response validator"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    import os
    import sys
    import argparse

    default_config = {
        "exporter": {
            "project_id": "",
            "credential": "",
        },
        "parser": {
            "filepath": "",
        },
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
    parser.add_argument(
        "--filepath",
        dest="filepath",
        default=default_config.get("filepath", ""),
        required=True,
        type=str,
        help="Path to the CSV file to parse.",
    )

    args, args_list = parser.parse_known_args()

    config = {
        "exporter": {
            "project_id": args.project_id,
            "credential": args.credential,
            "export_directory": args.export_directory,
            "export_filename": args.export_filename,
        },
        "parser": {
            "filepath": os.path.join(args.export_directory, args.export_filename),
        },
    }

    rr_validator = RichResponseValidator(config)
    rr_validator.run()
