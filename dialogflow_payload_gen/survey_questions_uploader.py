from copy import deepcopy
from typing import Dict

import __init__

from dialogflow_api.src import dialogflow as df

from dialogflow_payload_gen import SURVEY_METADATA_KEY

class SurveryQuestionsUploader:
    def __init__(self, config) -> None:
        self.config = config

        self.dialogflow = df.Dialogflow(config)
        self.dialogflow.get_intents()

        self.old_intents = None
        self.uploaded_intents = None

    def run(self, survey_questions_data=Dict[str, list]):

        if not survey_questions_data:
            survey_questions_data = self.config.get("survey_metadata")

        if not survey_questions_data:
            raise ValueError("Survey Metadata can not be empty!")

        intents = self.dialogflow.intents["display_name"]

        self.old_intents = deepcopy(intents)
        intents_to_upload = []

        for intent_name in intents:
            intent = intents[intent_name]

            survey_question_id = survey_questions_data.get(intent_name, None)
            if survey_question_id:
                cur_payload = intent.custom_payload
                cur_payload[SURVEY_METADATA_KEY] = {
                    "question_id": survey_question_id.question_id,
                    "question_text": survey_question_id.question_text,
                    "form": survey_question_id.question_form,
                }
                intent.custom_payload = cur_payload

                intents_to_upload.append(intent)

        #
        # # Prepare intents for upload
        # for intent_name in intents:
        #     intent_obj = intents[intent_name].intent_obj
        #     # Clear the followup_intent_info, otherwise dialogflow rejects the update
        #     while len(intent_obj.followup_intent_info) > 0:
        #         intent_obj.followup_intent_info.pop()
        #     # Clear root followup intent name, otherwise dialogflow rejects the update
        #     intent_obj.root_followup_intent_name = ""
        #     intent_obj.parent_followup_intent_name = ""

        self.dialogflow.batch_update_intents(
            [intent.intent_obj for intent in intents_to_upload]
        )

        self.uploaded_intents = intents_to_upload