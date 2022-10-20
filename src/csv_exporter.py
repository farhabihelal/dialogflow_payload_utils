from dataclasses import asdict, dataclass
from datetime import datetime
import os
from time import time
import spacy
from rich_response import RichFulfillmentSentence, RichFulfillmentText

import __init__

from dialogflow_api.src import dialogflow as df


@dataclass
class BaseRichDataClass:
    @classmethod
    def fromDict(self, obj: dict):
        return self(**obj)

    def toDict(self):
        return asdict(self)

    def tolist(self):
        return list(self.toDict().values())

    @classmethod
    def all_fields(self):
        return [x for x in self.__dataclass_fields__]


@dataclass
class DataRow(BaseRichDataClass):
    topic: str = ""
    intent: str = ""
    response: int = -1
    paraphrase: int = -1
    sentence: int = -1
    text: str = ""
    emotion: str = ""
    genre: str = ""
    routine: str = ""
    routine_id: int = -1
    comments: str = ""


class CSVExporter:
    def __init__(self, config) -> None:

        self._config = config

        self.dialogflow = df.Dialogflow(config)

        self.dialogflow.get_intents()
        self._nlp = spacy.load("en_core_web_sm")

        self.data = {}
        self.rows = []

    def run(self):
        self.load()
        self.gen_rows()
        self.dump()

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

    def dump(self):
        agent, ext = os.path.splitext(
            os.path.basename(self._config.get("credential", "default-agent.json"))
        )
        filename = agent + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ".tsv"
        dir = self._config.get("output_dir", f"{os.path.dirname(__file__)}")
        filepath = os.path.join(dir, filename)

        with open(filepath, "w") as f:
            lines = []

            header = DataRow.all_fields()
            lines.append("\t".join(header))

            for row in self.rows:
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

    args, args_list = parser.parse_known_args()

    config = {
        "project_id": args.project_id,
        "credential": args.credential,
    }

    parser = CSVExporter(config)
    parser.run()
