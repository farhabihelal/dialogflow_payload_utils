import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/.."))


from dialogflow_payload_gen.parser_xl import ParserXL
from dialogflow_payload_gen.rich_response_uploader import RichResponseUploader


class TestParseXLUpload:
    def __init__(self, config) -> None:
        self.config = config

        self.parser = ParserXL(config["parser"])
        self.uploader = RichResponseUploader(config["uploader"])

    def run(self):
        print("Parser is running...\t", end="")
        self.parser.run()
        print("done\n")

        print("Uploader is running...\t", end="")
        self.uploader.run(rich_responses=self.parser.parsed_data)
        print("done\n")

    def report(self):
        pass


if __name__ == "__main__":
    # title = "parse xl uploader "
    # version = "0.1.0"
    # author = "Farhabi Helal"
    # email = "farhabi.helal@jp.honda-ri.com"

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../..")
    data_dir = os.path.abspath(os.path.join(root_dir, "exports"))
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    # exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    # args = {
    #     "credential": os.path.abspath(os.path.join(agents_dir, "es.json")),
    #     "export_directory": exports_dir,
    #     "export_filename": "haru-games-annotated-after.tsv",
    #     "parse_filepath": os.path.join(
    #         exports_dir, "haru-games-annotated-modified.tsv"
    #     ),
    # }

    # agent_filename = "es.json"
    # agent_filename = "es2.json"
    # agent_filename = "child-in-hospital.json"
    # agent_filename = "child-in-hospital-2.json"
    # agent_filename = "system-intents.json"
    # agent_filename = "haru-test.json"
    agent_filename = "tiny-tiny-habits-rvuq.json"
    # agent_filename = "haru-smalltalk-all-topics-lithin.json"
    
    agent_name = os.path.splitext(agent_filename)[0]

    config = {
        "parser": {
            "filepath": os.path.join(data_dir, "tiny-tiny-habits-rvuq.xlsx"),
        },
        "uploader": {
            "credential": os.path.join(agents_dir, agent_filename),
            "language_code": "en",
        },
    }

    test = TestParseXLUpload(config)
    test.run()
    test.report()
