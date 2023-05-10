import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../dialogflow-api/src"))

from datetime import datetime

from exporter_xl import ExporterXL
from do.datarow_with_parent import DataRowWithParent

from dialogflow import Intent

import pandas as pd

import random


class ExporterXLWithParent(ExporterXL):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

    def gen_rows(self, data=None):
        data = data if data else self.data

        rows = []
        for key in data:
            for i, response in enumerate(data[key]):
                for j, text in enumerate(response):
                    for k, sentence in enumerate(text["sentences"]):
                        row: DataRowWithParent = self.behavior.add_behavior(
                            datarow=self.rfs_to_dr(sentence)
                        )
                        row.topic = self.dialogflow.intents["display_name"][
                            key
                        ].root.intent_obj.display_name
                        row.intent = key
                        row.parent = self.get_parent_question(key)
                        row.response = i + 1
                        row.paraphrase = j + 1
                        row.sentence = k + 1

                        rows.append(row)

        self.rows = rows

    def get_question_intent(self, intent: Intent) -> Intent:
        ref_intents = list(intent.references)
        if intent.parent:
            ref_intents.append(intent.parent)

        for ref in ref_intents:
            ref: Intent
            node_type = ref.custom_payload.get("node_type")
            if node_type and node_type in ["QuestionNode", "AnswerQuestionNode"]:
                return ref
            else:
                ref = self.get_question_intent(ref)
                if ref:
                    return ref

    def get_parent_question(self, intent_name: str) -> str:
        intent = self.dialogflow.intents["display_name"][intent_name]
        question_parent = self.get_question_intent(intent)

        if not question_parent:
            return ""

        response = ""
        for texts in question_parent.text_messages:
            response = " ".join([response, random.choice(texts)])
        return response.strip()

    def rfs_to_dr(self, rfs: dict) -> DataRowWithParent:
        """
        Converts Rich Fulfillment Sentence to DataRow.
        """
        dr = DataRowWithParent.fromDict(
            {k: v for k, v in rfs.items() if k in DataRowWithParent.all_fields()}
        )

        dr.routine_id = str(dr.routine)
        dr.routine = ""

        return dr

    def create_xlsx(self, sheets: dict, filepath: str = None):
        writer = pd.ExcelWriter(filepath)

        for sheet_name in sheets:
            df = pd.DataFrame(
                sheets[sheet_name], columns=DataRowWithParent.all_fields()
            )
            df.to_excel(
                excel_writer=writer,
                sheet_name=sheet_name,
                index=False,
            )

        writer.save()


if __name__ == "__main__":
    title = "csv exporter dfs"
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

    # config = {
    #     "project_id": args.project_id,
    #     "credential": args.credential,
    #     "export_directory": args.export_directory,
    #     "export_filename": args.export_filename,
    #     "algorithm": "dfs",
    # }

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    config = {
        # "credential": os.path.abspath(os.path.join(agents_dir, "es.json")),
        "credential": os.path.abspath(os.path.join(agents_dir, "haru-test.json")),
        # "credential": os.path.abspath(os.path.join(agents_dir, "system-intents.json")),
        "export_directory": exports_dir,
        "export_filename": "ES-with-parent.xlsx",
        "algorithm": "dfs",
        "mode": "text_rr",
    }

    exporter = ExporterXLWithParent(config)
    exporter.run()
