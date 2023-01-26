import os
import sys
from dialogflow_payload_gen import ASK_SURVEY_KEY
from dialogflow_payload_gen import SURVEY_METADATA_KEY
from dialogflow_payload_gen.do.survey_datarow import SurveyQuestionsDataRow

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from enum import Enum
from datetime import datetime
import spacy

from do.rich_response import (
    RichFulfillmentSentence,
    RichFulfillmentMessageCollection,
)
from do.base_datarow import DataRow

from dialogflow_api.src import dialogflow as df

from export_utils import ExportGeneric, ExportBFS, ExportDFS


class ExportMode(Enum):
    TEXT = 0
    RICH_RESPONSE = 1
    SURVEY_DATA = 2  # Loads survey question id
    SURVEY_QUESTIONS = 3  # Loads survey questions


class CSVExporter:
    def __init__(self, config: dict) -> None:

        self._config: dict = config

        self.dialogflow = df.Dialogflow(config)

        self.export_mode = self.get_export_mode()
        self.algo = self.get_export_algorithm()

        # self.dialogflow.get_intents()
        self._nlp = spacy.load("en_core_web_sm")

        self.data: dict = {}
        self.rows: list = []

        self.default_export_dir: str = os.path.abspath(
            f"{os.path.dirname(__file__)}/../exports"
        )

    def get_export_mode(self):
        mode = ExportMode.TEXT

        if self._config.get("mode", "") == "rich":
            mode = ExportMode.RICH_RESPONSE
        elif self._config.get("mode", "") == "survey":
            mode = ExportMode.SURVEY_DATA
        elif self._config.get("mode", "") == "survey_questions":
            mode = ExportMode.SURVEY_QUESTIONS

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

        mode = ExportMode.TEXT if not mode else mode

        if mode == ExportMode.RICH_RESPONSE:
            return self.load_rr()
        elif mode == ExportMode.SURVEY_DATA:
            return self.load_survey_data()
        elif mode == ExportMode.SURVEY_QUESTIONS:
            return self.load_survey_questions()

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

    def load_survey_data(self):
        data = {}
        intents = self.dialogflow.intents["display_name"]

        for key in intents:
            intent = intents[key]
            data[intent.intent_obj.display_name] = intent.custom_payload.get(ASK_SURVEY_KEY, "")

        self.data = data

    def load_survey_questions(self):
        data = {}
        intents = self.dialogflow.intents["display_name"]

        for key in intents:
            intent = intents[key]

            if 'node_type' in intent.custom_payload and intent.custom_payload['node_type'] == 'SurveyRootNode':
                for survey_question in intent.children:
                    data[survey_question.intent_obj.display_name] = {**{
                        'survey_root_name': intent.intent_obj.display_name,
                    }, **survey_question.custom_payload.get(SURVEY_METADATA_KEY, {})}

        self.data = data

    def gen_rows(self, data=None):

        data = data if data else self.data

        rows = []
        for key in data:

            if self.export_mode == ExportMode.SURVEY_QUESTIONS:
                survey_metadata = data[key]
                row = SurveyQuestionsDataRow(
                    survey_root_name=survey_metadata.get('survey_root_name', ""),
                    intent=key,
                    question_id=survey_metadata.get('question_id', ""),
                    question_text=survey_metadata.get('question_text', ""),
                    question_form=survey_metadata.get('form', ""),
                )
                rows.append(row)
            else:
                for i, response in enumerate(data[key]):
                    for j, text in enumerate(response):
                        for k, sentence in enumerate(text["sentences"]):
                            intent_obj = self.dialogflow.intents["display_name"][
                                key
                            ]

                            row = self.rfs_to_dr(sentence)
                            row.topic = intent_obj.root.intent_obj.display_name
                            row.intent = key
                            row.response = i + 1
                            row.paraphrase = j + 1
                            row.sentence = k + 1
                            if row.response == row.paraphrase == row.sentence == 1:
                                row.survey_question_id = int(intent_obj.custom_payload.get(ASK_SURVEY_KEY, None)) \
                                    if intent_obj.custom_payload.get(ASK_SURVEY_KEY, None) else ""

                            rows.append(row)

        self.rows = rows

    def get_processed_data(self, rows=None) -> list:

        rows = rows if rows else self.rows

        lines = []

        if self.export_mode == ExportMode.SURVEY_QUESTIONS:
            header = SurveyQuestionsDataRow.all_fields()
            lines.append("\t".join(header))
            rows = sorted(rows, key=lambda x: x.question_id)

            for row in rows:
                row: SurveyQuestionsDataRow
                line = row.tolist()
                lines.append("\t".join([str(x) for x in line]))
        else:
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

    def rfs_to_dr(self, rfs: dict):
        """
        Converts Rich Fulfillment Sentence to DataRow.
        """
        return DataRow.fromDict(
            {k: v for k, v in rfs.items() if k in DataRow.all_fields()}
        )


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

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/..")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    config = {
        "project_id": "empathetic-stimulator-owp9",
        "credential": os.path.abspath(os.path.join(agents_dir, "es.json")),
        "export_directory": exports_dir,
        "export_filename": "es.tsv",
        "algorithm": "dfs",
        "mode": "text",
    }

    exporter = CSVExporter(config)
    exporter.run()
