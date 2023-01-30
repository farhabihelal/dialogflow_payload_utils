from copy import deepcopy
from typing import Dict

import __init__

from dialogflow_api.src import dialogflow as df

from dialogflow_payload_gen import ASK_SURVEY_KEY


class SurveyMetadataUploader:
    def __init__(self, config) -> None:
        self.config = config

        self.dialogflow = df.Dialogflow(config)
        self.dialogflow.get_intents()

        self.old_intents = None
        self.uploaded_intents = None

    def run(self, survey_data=Dict[str, dict]):

        if not survey_data:
            survey_data = self.config.get("survey_metadata")

        if not survey_data:
            raise ValueError("Survey Metadata can not be empty!")

        intents = self.dialogflow.intents["display_name"]

        self.old_intents = deepcopy(intents)

        for intent_name in intents:
            intent = intents[intent_name]

            survey_question_id = survey_data.get(intent_name, None)
            if survey_question_id:
                cur_payload = intent.custom_payload
                cur_payload[ASK_SURVEY_KEY] = int(survey_question_id)
                intent.custom_payload = cur_payload

        self.dialogflow.batch_update_intents(
            [intents[intent_name].intent_obj for intent_name in intents]
        )

        self.uploaded_intents = intents


if __name__ == "__main__":

    title = "survey metadata uploader"
    version = "0.1.0"
    author = "Levko Ivanchuk"
    email = "levko@livanchuk.com"

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

    survey_metadata_uploader = SurveyMetadataUploader(config)
    survey_metadata_uploader.run()
