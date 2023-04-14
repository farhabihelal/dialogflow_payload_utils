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
    data_dir = os.path.abspath(os.path.join(root_dir, "data"))

    from es_data import session_data

    # agent_filename = "es.json"
    # agent_filename = "es2.json"
    # agent_filename = "child-in-hospital.json"
    # agent_filename = "child-in-hospital-2.json"
    # agent_filename = "system-intents.json"
    agent_filename = "haru-test.json"
    agent_name = os.path.splitext(agent_filename)[0]

    config = {
        "parser": {
            "filepath": os.path.join(data_dir, "ES_GS_D2S2.xlsx"),
            "session_data": session_data[agent_name],
            # "session_data": session_data['es'],
        },
        "uploader": {
            "credential": os.path.join(agents_dir, agent_filename),
            "language_code": "en",
        },
    }

    test = ESUploader(config)
    test.run()
    test.report()
