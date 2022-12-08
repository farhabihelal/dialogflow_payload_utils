import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/.."))

from dialogflow_payload_gen.csv_exporter import ExportMode

from dialogflow_payload_gen.csv_exporter import CSVExporter
from dialogflow_payload_gen.csv_exporter_bfs import CSVExporterBFS
from dialogflow_payload_gen.csv_exporter_dfs import CSVExporterDFS
from dialogflow_payload_gen.csv_exporter_xl import CSVExporterXL


class TestExport:
    def __init__(self, config) -> None:
        self.config = config

        self.select_exporter()

    def select_exporter(self):
        if self.config.get("exporter_name", "") == "bfs":
            exporter = CSVExporterBFS(config["exporter"])

        elif self.config.get("exporter_name", "") == "dfs":
            exporter = CSVExporterDFS(config["exporter"])

        elif self.config.get("exporter_name", "") == "xl":
            exporter = CSVExporterXL(config["exporter"])

        else:
            exporter = CSVExporter(config["exporter"])

        self.exporter = exporter

    def run(self):

        print("Exporter is running...\t", end="")
        self.exporter.run(export_mode=ExportMode.RICH_RESPONSE)
        print("done\n")

    def report(self):
        pass


if __name__ == "__main__":

    title = "rich response validator"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/..")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    args = {
        "project_id": "api-test-v99y",
        "credential": os.path.abspath(os.path.join(agents_dir, "api-test.json")),
        "export_directory": exports_dir,
    }

    config = {
        "exporter_name": "dfs",
        "exporter": {
            "project_id": args["project_id"],
            "credential": args["credential"],
            "export_directory": args["export_directory"],
        },
    }

    test = TestExport(config)
    test.run()
    test.report()
