import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../.."))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))


from hc_parser import HCParser
from dialogflow_payload_gen.rich_response_uploader import RichResponseUploader


class HCUploader:
    def __init__(self, config) -> None:
        self.config = config

        self.parser = HCParser(config["parser"])
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
    title = "haru chat uploader"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    config = {
        "parser": {
            "filepath": os.path.join(exports_dir, "Haru-Chat-Games.xlsx"),
        },
        "uploader": {
            # "project_id": "haru-smalltalk-all-topics-girm",
            "credential": os.path.join(agents_dir, "haru-chat-games.json"),
        },
    }

    uploader = HCUploader(config)
    uploader.run()
    uploader.report()
