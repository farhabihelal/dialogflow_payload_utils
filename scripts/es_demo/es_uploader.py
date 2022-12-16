import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../.."))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))


from es_parser import ESParser
from dialogflow_payload_gen.rich_response_uploader import RichResponseUploader


class ESUploader:
    def __init__(self, config) -> None:
        self.config = config

        self.parser = ESParser(config["parser"])
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

    title = "es uploader"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    from es_data import session_data

    config = {
        "parser": {
            "filepath": os.path.join(exports_dir, "ES.xlsx"),
            "session_data": session_data,
        },
        "uploader": {
            "project_id": "empathetic-stimulator-owp9",
            "credential": os.path.join(agents_dir, "es.json"),
        },
    }

    test = ESUploader(config)
    test.run()
    test.report()
