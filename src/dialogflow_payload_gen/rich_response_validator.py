from dialogflow_payload_gen.exporter import Exporter
from parser import Parser
from rich_response_uploader import RichResponseUploader


class RichResponseValidator:
    def __init__(self, config) -> None:
        self.config = config

        self.exporter = Exporter(config["exporter"])

        self.parser = Parser(config["parser"])

        self.uploader = RichResponseUploader(config["uploader"])

        self.ignored_intents = []
        self.faulty_intents = []

    def run(self):
        self.exporter.run()
        self.parser.run()

        exporter_data = self.exporter.rich_responses
        parser_data = self.parser.parsed_data

        for k in exporter_data:
            exporter_rr = exporter_data[k]

            # ignore intents that don't have responses. These are missing in the csv.
            if not bool(exporter_rr):
                self.ignored_intents.append(k)
                continue

            parser_rr = parser_data[k]

            if exporter_rr != parser_rr:
                self.faulty_intents.append(
                    {"intent": k, "exporter_rr": exporter_rr, "parser_rr": parser_rr}
                )

            # hash_exporter = hash(repr(exporter_rr))
            # hash_parser = hash(repr(parser_rr))

            # if hash_exporter != hash_parser:
            #     self.faulty_intents.append(
            #         {"intent": k, "exporter_rr": exporter_rr, "parser_rr": parser_rr}
            #     )

    def upload(self):
        pass

    def export(self):
        self.exporter.run()

    def report(self):
        print(f"intents ignored : {len(self.ignored_intents)}")
        print(f"intents faulty  : {len(self.faulty_intents)}")


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
        "uploader": {
            "project_id": "",
            "credential": "",
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
        help="Path to the  file to parse.",
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
        "uploader": {
            "project_id": args.project_id,
            "credential": args.credential,
        },
    }

    rr_validator = RichResponseValidator(config)
    rr_validator.run()
    rr_validator.report()
