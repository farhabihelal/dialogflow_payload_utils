import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/.."))


from dialogflow_payload_gen.parser import Parser
from dialogflow_payload_gen.rich_response_uploader import RichResponseUploader


class TestParseUpload:
    def __init__(self, config) -> None:
        self.config = config

        self.parser = Parser(config["parser"])
        self.uploader = RichResponseUploader(config["uploader"])

    def run(self):

        print("Parser is running...\t", end="")
        self.parser.run(
            filepath=os.path.join(
                self.config["exporter"]["export_directory"],
                "d1-intro-outro-transitions.csv",
            )
        )
        print("done\n")

        print("Uploader is running...\t", end="")
        self.uploader.run(rich_responses=self.parser.parsed_data)
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
        "project_id": "empathetic-stimulator-owp9",
        "credential": os.path.abspath(os.path.join(agents_dir, "es.json")),
        "export_directory": exports_dir,
        "export_filename": "haru-games-annotated-after.tsv",
        "parse_filepath": os.path.join(
            exports_dir, "haru-games-annotated-modified.tsv"
        ),
    }

    config = {
        "exporter": {
            "project_id": args["project_id"],
            "credential": args["credential"],
            "export_directory": args["export_directory"],
            "export_filename": args["export_filename"],
        },
        "parser": {
            "filepath": os.path.abspath(
                os.path.join(args["export_directory"], args["export_filename"])
            ),
        },
        "uploader": {
            "project_id": args["project_id"],
            "credential": args["credential"],
        },
    }

    test = TestParseUpload(config)
    test.run()
    test.report()
