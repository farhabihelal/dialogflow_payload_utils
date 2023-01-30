import os

from dialogflow_payload_gen.csv_parser import CSVParser
from dialogflow_payload_gen.survey_questions_parser import SurveyQuestionsParser
from dialogflow_payload_gen.survey_questions_uploader import SurveryQuestionsUploader


class TestSurveyQuestionsUpload:
    def __init__(self, config) -> None:
        self.config = config

        self.parser = SurveyQuestionsParser(config["parser"])
        self.uploader = SurveryQuestionsUploader(config["uploader"])

    def run(self):

        print("Parser is running...\t", end="")
        self.parser.run()
        print("done\n")

        print("Uploader is running...\t", end="")
        self.uploader.run(survey_questions_data=self.parser.parsed_data)
        print("done\n")

    def report(self):
        pass

if __name__ == "__main__":

    title = "rich response validator"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/..")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    args = {
        "project_id": "hospital-surveyor-agent-hwdb",
        "credential": os.path.abspath(os.path.join(agents_dir, "hsa.json")),
        "export_directory": exports_dir,
        "parse_filepath": os.path.join(exports_dir, "hsa.tsv"),
        "mode": "questions"
    }

    config = {
        "parser": {
            "filepath": args["parse_filepath"],
        },
        "rr_uploader": {
            "project_id": args["project_id"],
            "credential": args["credential"],
        },
        "uploader": {
            "project_id": args["project_id"],
            "credential": args["credential"],
        },
    }

    test = TestSurveyQuestionsUpload(config)
    test.run()
    test.report()