import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../.."))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))


from dialogflow_payload_gen.rich_response_uploader import RichResponseUploader


class MetadataUpdater:
    def __init__(self, config) -> None:
        self.config = config

        self.parser = config["parser"]
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
    title = "metadata updater"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))
    data_dir = os.path.abspath(os.path.join(root_dir, "data"))

    from dialogflow_payload_gen.parser_xl import ParserXL

    config = {
        "parser": ParserXL(
            {
                "filepath": os.path.join(exports_dir, "System-Intents.xlsx"),
            }
        ),
        "uploader": {
            "credential": os.path.join(agents_dir, "es.json"),
            # "credential": os.path.join(agents_dir, "child-in-hospital.json"),
            # "credential": os.path.join(agents_dir, "haru-test.json"),
            # "credential": os.path.join(agents_dir, "system-intents.json"),
            "language_code": "en",
        },
    }

    test = MetadataUpdater(config)
    test.run()
    test.report()
