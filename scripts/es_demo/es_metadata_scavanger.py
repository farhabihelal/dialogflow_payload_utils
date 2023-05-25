import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../.."))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))

sys.path.append(
    os.path.abspath(f"{os.path.dirname(__file__)}/../../src/dialogflow-api/src")
)

from dialogflow import Dialogflow, Intent
from es_parser import ESParser
from dialogflow_payload_gen.rich_response_uploader import RichResponseUploader
from dialogflow_payload_gen.do.rich_response import (
    RichFulfillmentMessageCollection,
    RichFulfillmentContainer,
    RichFulfillmentText,
    RichFulfillmentSentence,
)


class ESMetadataScavanger:
    def __init__(self, config: dict) -> None:
        self.configure(config)

        self.api = Dialogflow(config)
        self.uploader = RichResponseUploader(config)

        self._index = {}

    def configure(self, config: dict):
        self.config = config
        self.parser: ESParser = config["parser"]

    def run(self):
        print("Loading data from Dialogflow...\t", end="")
        self.api.get_intents(language_code=self.config.get("language_code"))
        self.api.generate_tree()
        print("done\n")

        print("Parser is running...\t", end="")
        self.parser.run()
        print("done\n")

        print("Building index...\t", end="")
        self.build_index()
        print("done\n")

        print("Scavanger is running...\t", end="")
        self.scavange()
        print("done\n")

        print("Uploader is running...\t", end="")
        self.uploader.run(rich_responses=self.parser.parsed_data)
        print("done\n")

    def build_index(self, parsed_data: dict = None) -> dict:
        parsed_data = parsed_data if parsed_data else self.parser.parsed_data
        index = {}

        for rfmc in parsed_data.values():
            rfmc: RichFulfillmentMessageCollection
            for rfc in rfmc:
                rfc: RichFulfillmentContainer
                for rft in rfc:
                    rft: RichFulfillmentText
                    for rfs in rft.sentences:
                        rfs: RichFulfillmentSentence
                        index[rfs.text] = rfs

        self._index = index
        return index

    def scavange(self, intents: list, index: dict):
        intents = intents if intents else self.api.intents["display_name"]
        pass


if __name__ == "__main__":
    title = "es metadata scavanger"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))
    data_dir = os.path.abspath(os.path.join(root_dir, "data"))

    from es_data import session_data

    # agent_filename = "es.json"
    agent_filename = "es2.json"
    # agent_filename = "child-in-hospital.json"
    # agent_filename = "child-in-hospital-2.json"
    # agent_filename = "system-intents.json"
    # agent_filename = "haru-test.json"
    agent_name = os.path.splitext(agent_filename)[0]

    session_data = session_data["es2"]
    config = {
        "parser": ESParser(
            {
                "filepath": os.path.join(root_dir, "exports", "ES_D[4-5].xlsx"),
                "session_data": session_data,
            }
        ),
        "session_data": session_data,
        "credential": os.path.join(agents_dir, agent_filename),
        "language_code": "en",
    }

    scavanger = ESMetadataScavanger(config)
    scavanger.run()
