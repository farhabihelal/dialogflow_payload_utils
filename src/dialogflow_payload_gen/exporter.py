import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../dialogflow-api/src"))

from enum import Enum
from datetime import datetime
from time import time
import spacy

from do.base_rich_dataclass import BaseRichDataClass
from do.rich_response import (
    RichFulfillmentSentence,
    RichFulfillmentText,
    RichFulfillmentContainer,
    RichFulfillmentMessageCollection,
)
from do.base_datarow import DataRow
from behavior import Behavior

from dialogflow import Dialogflow

from export_utils import ExportGeneric, ExportBFS, ExportDFS


class ExportMode(Enum):
    TEXT = 0
    RICH_RESPONSE = 1
    TEXT_RR = 2


class Exporter:
    def __init__(self, config: dict) -> None:
        self._config: dict = config

        self.dialogflow = Dialogflow(config)

        self.behavior = Behavior(config["behavior"])

        self.export_mode = self.get_export_mode()
        self.algo = self.get_export_algorithm()

        # self.dialogflow.get_intents()
        self._nlp = spacy.load("en_core_web_sm")

        self.data: dict = {}
        self.rows: list = []

        self._annotation_data: dict = {}

        self.default_export_dir: str = os.path.abspath(
            f"{os.path.dirname(__file__)}/../exports"
        )

    def get_export_mode(self):
        mode = ExportMode.TEXT

        if self._config.get("mode", "") == "rich":
            mode = ExportMode.RICH_RESPONSE
        elif self._config.get("mode", "") == "text_rr":
            mode = ExportMode.TEXT_RR

        return mode

    def get_export_algorithm(self):
        algo = None

        if self._config.get("algorithm") == "bfs":
            algo = ExportBFS()

        elif self._config.get("algorithm") == "dfs":
            algo = ExportDFS()

        else:
            algo = ExportGeneric()

        return algo

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

    def run(self, export_filename=None, export_mode=None):
        export_mode = export_mode if export_mode else self.export_mode
        export_filename = (
            export_filename if export_filename else self._config.get("export_filename")
        )

        self.load(mode=export_mode)
        self.gen_rows(
            data=self.algo.get_data(self.data, self.dialogflow.get_root_intents())
        )
        self.dump(lines=self.get_processed_data(), filename=export_filename)

    def load(self, mode=None):
        self.dialogflow.get_intents()
        self.dialogflow.generate_tree()

        self.load_annotations()

        mode = ExportMode.TEXT if not mode else mode

        if mode == ExportMode.RICH_RESPONSE:
            return self.load_rr()
        elif mode == ExportMode.TEXT_RR:
            return self.load_text_rr()

        return self.load_text()

    def load_text(self):
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

    def load_rr(self):
        data = {}
        intents = self.dialogflow.intents["display_name"]

        for key in intents:
            intent = intents[key]
            data[intent.intent_obj.display_name] = intent.rich_responses

        self.data = data

    def load_text_rr(self, threshold: float = 0.8):
        data = {}
        intents = self.dialogflow.intents["display_name"]

        for key in intents:
            intent = intents[key]
            rich_responses = RichFulfillmentMessageCollection.from_text_messages(
                intent.text_messages
            )

            rich_responses_payload = RichFulfillmentMessageCollection(
                intent.rich_responses
            )

            for i, rfc in enumerate(rich_responses):
                rfc: RichFulfillmentContainer
                for j, rft in enumerate(rfc):
                    rft: RichFulfillmentText
                    for k, rfs in enumerate(rft.sentences):
                        rfs: RichFulfillmentSentence
                        rfs_payload: RichFulfillmentSentence = (
                            rich_responses_payload.get_fulfillment_sentence(
                                sentence=rfs.text, threshold=threshold
                            )
                        )

                        if rfs_payload:
                            # Replace ONLY annotations NOT Text
                            if not rich_responses[i][j].sentences[k].auto_score:
                                rich_responses[i][j].sentences[
                                    k
                                ].auto_score = rfs_payload.auto_score

                            if not rich_responses[i][j].sentences[k].auto_emotion:
                                rich_responses[i][j].sentences[
                                    k
                                ].auto_emotion = rfs_payload.auto_emotion

                            if not rich_responses[i][j].sentences[k].auto_genre:
                                rich_responses[i][j].sentences[
                                    k
                                ].auto_genre = rfs_payload.auto_genre

                            if not rich_responses[i][j].sentences[k].emotion:
                                rich_responses[i][j].sentences[
                                    k
                                ].emotion = rfs_payload.emotion

                            if not rich_responses[i][j].sentences[k].genre:
                                rich_responses[i][j].sentences[
                                    k
                                ].genre = rfs_payload.genre

                            if not rich_responses[i][j].sentences[k].routine:
                                rich_responses[i][j].sentences[
                                    k
                                ].routine = rfs_payload.routine

                            if not rich_responses[i][j].sentences[k].silence:
                                rich_responses[i][j].sentences[
                                    k
                                ].silence = rfs_payload.silence

            data[intent.intent_obj.display_name] = rich_responses.toDict()["messages"]

        self.data = data

    def load_annotations(self):
        data = {}
        intents = self.dialogflow.intents["display_name"]

        for key in intents:
            intent = intents[key]
            rich_responses = RichFulfillmentMessageCollection(intent.rich_responses)

            if not rich_responses:
                continue

            for i, rfc in enumerate(rich_responses):
                rfc: RichFulfillmentContainer
                for j, rft in enumerate(rfc):
                    rft: RichFulfillmentText
                    for k, rfs in enumerate(rft.sentences):
                        rfs: RichFulfillmentSentence
                        key = f"{rfs.text}-{intent.display_name}-{i}-{j}-{k}"
                        data[key] = rfs

        self._annotation_data = data

    def gen_rows(self, data=None):
        data = data if data else self.data

        rows = []
        for key in data:
            for i, response in enumerate(data[key]):
                for j, text in enumerate(response):
                    for k, sentence in enumerate(text["sentences"]):
                        row = self.behavior.add_behavior(
                            datarow=self.rfs_to_dr(sentence)
                        )
                        row.topic = self.dialogflow.intents["display_name"][
                            key
                        ].root.intent_obj.display_name
                        row.intent = key
                        row.response = i + 1
                        row.paraphrase = j + 1
                        row.sentence = k + 1

                        rows.append(row)

        self.rows = rows

    def get_processed_data(self, rows=None) -> list:
        rows = rows if rows else self.rows

        lines = []

        header = DataRow.all_fields()
        lines.append("\t".join(header))

        rows = sorted(rows, key=lambda x: x.topic)

        for row in rows:
            row: DataRow
            line = row.tolist()
            lines.append("\t".join([str(x) for x in line]))

        return lines

    def dump(self, lines=None, filename=None):
        if not lines:
            raise ValueError("Lines can not be empty!")

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
            f.writelines([f"{x}\n" for x in lines])

    # def rfs_to_dr(self, rfs: dict):
    #     """
    #     Converts Rich Fulfillment Sentence to DataRow.
    #     """
    #     return DataRow.fromDict(
    #         {k: v for k, v in rfs.items() if k in DataRow.all_fields()}
    #     )

    def rfs_to_dr(self, rfs: dict):
        """
        Converts Rich Fulfillment Sentence to DataRow.
        """
        dr = DataRow.fromDict(
            {k: v for k, v in rfs.items() if k in DataRow.all_fields()}
        )

        dr.routine_id = str(dr.routine)
        dr.routine = ""

        return dr


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
        "algorithm": "",
        "mode": "text",
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

    # config = {
    #     "project_id": args.project_id,
    #     "credential": args.credential,
    #     "export_directory": args.export_directory,
    #     "export_filename": args.export_filename,
    #     "algorithm": "dfs",
    #     "mode": "text",
    # }

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    config = {
        "credential": os.path.abspath(os.path.join(agents_dir, "es.json")),
        "export_directory": exports_dir,
        "export_filename": "es.tsv",
        "algorithm": "dfs",
        "mode": "text_rr",
        "behavior": {
            "override_behavior": False,
            "profile": {},
        },
    }

    exporter = Exporter(config)
    exporter.run()
