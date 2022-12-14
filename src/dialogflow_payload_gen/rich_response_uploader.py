import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../dialogflow_api/src"))

from copy import deepcopy


from dialogflow import Dialogflow


class RichResponseUploader:
    def __init__(self, config) -> None:
        self.config = config

        self.dialogflow = Dialogflow(config)
        self.dialogflow.get_intents()

        self.old_intents = None
        self.uploaded_intents = None

    def run(self, rich_responses=None):

        if not rich_responses:
            rich_responses = self.config.get("rich_responses")

        if not rich_responses:
            raise ValueError("Rich Responses can not be empty!")

        intents = self.dialogflow.intents["display_name"]

        self.old_intents = deepcopy(intents)

        for intent_name in intents:
            intent = intents[intent_name]

            rr = rich_responses.get(intent_name)
            if rr:
                intent.rich_responses = rr

        self.dialogflow.batch_update_intents(
            [intents[intent_name].intent_obj for intent_name in intents]
        )

        self.uploaded_intents = intents


if __name__ == "__main__":

    title = "rich response uploader"
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

    rr_uploader = RichResponseUploader(config)
    rr_uploader.run()
