from dialogflow_payload_gen.csv_parser import CSVParser
from dialogflow_payload_gen.do.survey_datarow import SurveyQuestionsDataRow


class SurveyQuestionsParser(CSVParser):
    """A parser for survey questions."""

    def __init__(self, config) -> None:
        super().__init__(config)

    def parse(self):
        """Parse the survey questions data."""
        parsed_data = {}

        for intent in self.intent_names:
            row = next(iter(self.get_intent_rows(intent)), None)
            if row is None:
                continue

            parsed_data[intent] = SurveyQuestionsDataRow(
                survey_root_name=row[self._header_map["survey_root_name"]],
                intent=row[self._header_map["intent"]],
                question_id=row[self._header_map["question_id"]],
                question_text=row[self._header_map["question_text"]],
                question_form=row[self._header_map["question_form"]],
            )

        self.parsed_data = parsed_data


    def report(self):
        """Report the parsing result."""
        print(f"Survey questions parsed: {len(self.parsed_data)}")

