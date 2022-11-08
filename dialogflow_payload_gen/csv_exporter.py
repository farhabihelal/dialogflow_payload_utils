import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from datetime import datetime
from time import time
import spacy

from do.base_rich_dataclass import BaseRichDataClass
from do.rich_response import (
    RichFulfillmentSentence,
    RichFulfillmentMessageCollection,
)
from do.base_datarow import DataRow


import __init__

from dialogflow_api.src import dialogflow as df


class CSVExporter:
    def __init__(self, config: dict) -> None:

        self._config: dict = config

        self.dialogflow = df.Dialogflow(config)

        self.dialogflow.get_intents()
        self._nlp = spacy.load("en_core_web_sm")

        self.data: dict = {}
        self.rows: list = []

        self.default_export_dir: str = os.path.abspath(
            f"{os.path.dirname(__file__)}/../exports"
        )

    @property
    def sorted_data(self) -> dict:
        return {k: self.data[k] for k in sorted(self.data.keys())} if self.data else {}

    @property
    def rich_responses(self) -> RichFulfillmentMessageCollection:
        rich_responses = {
            k: RichFulfillmentMessageCollection.from_payload({"messages": v})
            for k, v in self.sorted_data.items()
        }

        return rich_responses

    def run(self, export_filename=None):
        self.load()
        self.gen_rows()
        self.dump(filename=export_filename)

    def load(self):
        data = {}
        intents = self.dialogflow.intents["display_name"]

        for key in intents:
            intent = intents[key]

            containers = []
            for text_container in intent.text_messages:
                texts = []
                for text in text_container:
                    sentence_container = {"text": text}
                    nlp_result = self._nlp(text.replace('"', ""))
                    sentences = []
                    for sent in nlp_result.sents:
                        rfs = RichFulfillmentSentence(text=sent.text)
                        sentences.append(rfs.toDict())
                    sentence_container["sentences"] = sentences
                    texts.append(sentence_container)
                containers.append(texts)
            data[intent.intent_obj.display_name] = containers

        self.data = data

    def gen_rows(self):

        rows = []
        for key in self.data:
            for i, response in enumerate(self.data[key]):
                for j, text in enumerate(response):
                    for k, sentence in enumerate(text["sentences"]):

                        row = DataRow()
                        row.intent = key
                        row.response = i + 1
                        row.paraphrase = j + 1
                        row.sentence = k + 1
                        row.text = sentence["text"]
                        # row.emotion = key
                        # row.genre = "neutral"
                        # row.routine = key
                        # row.routine_id = key
                        # row.comments = key

                        rows.append(row)

        self.rows = rows

    def dump(self, filename=None):
        agent, ext = os.path.splitext(
            os.path.basename(self._config.get("credential", "default-agent.json"))
        )
        datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = (
            filename
            if bool(filename)
            else self._config.get("export_filename")
            if bool(self._config.get("export_filename"))
            else f"{agent}_{datetime_str}.tsv"
        )
        dir = (
            self._config.get("export_directory")
            if bool(self._config.get("export_directory"))
            else self.default_export_dir
        )
        os.makedirs(dir, exist_ok=True)
        filepath = os.path.join(dir, filename)

        with open(filepath, "w") as f:
            lines = []

            header = DataRow.all_fields()
            lines.append("\t".join(header))

            rows = sorted(self.rows, key=lambda x: x.intent)

            for row in rows:
                line = row.tolist()
                lines.append("\t".join([str(x) for x in line]))

            f.writelines([f"{x}\n" for x in lines])


if __name__ == "__main__":

    title = "csv exporter"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    import argparse

    default_config = {
        "project_id": "",
        "credential": "",
        "export_directory": "",
        "export_filename": "",
    }

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--project_id",
        dest="project_id",
        type=str,
        default=default_config.get("project_id", ""),
        help="Google Cloud Project Id",
    )
    parser.add_argument(
        "--credential",
        dest="credential",
        type=str,
        default=default_config.get("credential", ""),
        help="Path to Google Cloud Project credential",
    )
    parser.add_argument(
        "--export_directory",
        dest="export_directory",
        type=str,
        default=default_config.get("export_directory", ""),
        help="Absolute path to export directory",
    )
    parser.add_argument(
        "--export_filename",
        dest="export_filename",
        type=str,
        default=default_config.get("export_filename", ""),
        help="Name of the exported file",
    )

    args, args_list = parser.parse_known_args()

    config = {
        "project_id": args.project_id,
        "credential": args.credential,
        "export_directory": args.export_directory,
        "export_filename": args.export_filename,
    }

    exporter = CSVExporter(config)
    exporter.run()
