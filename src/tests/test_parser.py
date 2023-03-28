import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/.."))


from dialogflow_payload_gen.parser import Parser
from dialogflow_payload_gen.parser_xl import ParserXL


class TestParser:
    def __init__(self, config: dict) -> None:
        self.config = config

        self.parser = Parser(config["parser"])

        self.select_parser()

    def select_parser(self):

        if self.config.get("parser_name") == "xl":
            parser = ParserXL(self.config["parser"])
        else:
            parser = Parser(config["parser"])

        self.parser = parser

    def run(self):

        print("Parser is running...\t", end="")
        self.parser.run()
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
        "export_filename": "haru-test.tsv",
        "parse_filepath": os.path.join(exports_dir, "haru-test.xlsx"),
    }

    config = {
        "parser_name": "xl",
        "parser": {
            "filepath": args["parse_filepath"],
        },
    }

    test = TestParser(config)
    test.run()
    test.report()
