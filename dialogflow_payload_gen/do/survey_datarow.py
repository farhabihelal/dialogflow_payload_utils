from dataclasses import dataclass

from dialogflow_payload_gen.do.base_rich_dataclass import BaseRichDataClass


@dataclass
class SurveyQuestionsDataRow(BaseRichDataClass):
    """A row in a survey questions database."""
    survey_root_name: str  # The survey root name
    intent: str  # The question intent name
    question_id: str  # The question ID
    question_text: str  # The question text
    question_form: str  # The question form
