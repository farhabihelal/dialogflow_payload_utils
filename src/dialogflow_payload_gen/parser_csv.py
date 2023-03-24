import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


import pandas as pd

from do.rich_response import (
    RichFulfillmentSentence,
    RichFulfillmentText,
    RichFulfillmentMessageCollection,
    RichFulfillmentContainer,
)

from do.base_datarow import DataRow

from dialogflow_payload_gen.behavior import Behavior


class ParserCSV:
    def __init__(self, config: dict) -> None:
        super().__init__(config)

        self._csv = None

    def load(self, filepath=None):
        self._csv = pd.read_csv(
            filepath if bool(filepath) else self._config["filepath"], sep="\t", header=0
        )
        self._csv.fillna("", inplace=True)
        self._data = self._csv.values.tolist()
        self._header = self._csv.columns.values.tolist()
        self._header_map = {header: i for i, header in enumerate(self._header)}
        self.unique_intents = self.get_unique_intents()
        self.intent_names = list(self.unique_intents.keys())


if __name__ == "__main__":
    title = "csv parser"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    import argparse

    default_config = {
        "filepath": "",
    }

    parser = argparse.ArgumentParser()

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
        "filepath": args.filepath,
        "behavior": {
            "override_behavior": False,
            "override_intent_names": [],
            "profile": {},
        },
    }

    parser = ParserCSV(config)
    parser.run()
    data = parser.parsed_data
    print(data)
