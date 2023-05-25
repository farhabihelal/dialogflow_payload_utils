import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))
sys.path.append(
    os.path.abspath(f"{os.path.dirname(__file__)}/../../src/dialogflow-api/src")
)

from copy import deepcopy


from dialogflow import Dialogflow, Intent

from dialogflow_payload_gen.rich_response_uploader import RichResponseUploader
from dialogflow_payload_gen.do.rich_response import (
    RichFulfillmentMessageCollection,
    RichFulfillmentText,
    RichFulfillmentContainer,
    RichFulfillmentSentence,
)


class HaruGamesRichResponseUploader(RichResponseUploader):
    def __init__(self, config) -> None:
        super().__init__(config)

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
                rr = self.handle_special_intent(intent, rr)
                intent.rich_responses = rr

        print("Backing up...\t", end="")
        self.dialogflow.create_version(
            f"backup before updating metadata from api.".title()
        )
        print("done\n")

        self.dialogflow.batch_update_intents(
            [intents[intent_name].intent_obj for intent_name in intents],
            self.config.get("language_code"),
        )

        self.uploaded_intents = intents

    def handle_special_intent(
        self, intent: Intent, rr: RichFulfillmentMessageCollection
    ) -> dict:
        if "madlibs" in intent.display_name:
            return self.handle_madlibs(intent, rr)

        elif all(x in intent.display_name for x in ["jokes", "compressed"]):
            return self.handle_humor(intent, rr)

        elif all(x in intent.display_name for x in ["trivia", "compressed"]):
            return self.handle_trivia(intent, rr)

        return rr

    def handle_madlibs(
        self, intent: Intent, rr: RichFulfillmentMessageCollection
    ) -> dict:
        # handle hand implemented type
        if "create-madlibs" in intent.display_name and len(intent.children) > 0:
            for rfc in rr:
                rfc: RichFulfillmentContainer
                rft: RichFulfillmentText = rfc[0]
                last_sentence: RichFulfillmentSentence = rft.sentences[-1]
                last_sentence.routine = self.get_routine(last_sentence)
                break

        # handle auto generated type
        elif (
            "-madlib" in intent.display_name
            and len(intent.children) == 0
            and "create-madlibs" not in intent.display_name
        ):
            for rfc in rr:
                rfc: RichFulfillmentContainer
                for rft in rfc:
                    rft: RichFulfillmentText
                    last_sentence: RichFulfillmentSentence = rft.sentences[-1]
                    last_sentence.routine = self.get_routine(last_sentence)

        return rr

    def handle_humor(
        self, intent: Intent, rr: RichFulfillmentMessageCollection
    ) -> dict:
        humor_root_intent: Intent = self.dialogflow.intents["display_name"][
            "humor-data-compressed"
        ]

        # if intent.display_name in [x.display_name for x in humor_root_intent.children]:
        #     return

        # validate intent is leaf
        if len(intent.children) > 0:
            return

        if intent.display_name == "kid-jokes-compressed-002":
            print()

        for rfc in rr:
            rfc: RichFulfillmentContainer
            for rft in rfc:
                rft: RichFulfillmentText
                last_sentence: RichFulfillmentSentence = rft.sentences[-1]
                last_sentence.routine = self.get_routine(last_sentence)

        return rr

    def handle_trivia(
        self, intent: Intent, rr: RichFulfillmentMessageCollection
    ) -> dict:
        trivia_root_intent: Intent = self.dialogflow.intents["display_name"][
            "trivia-data-compressed"
        ]

        # if intent.display_name in [x.display_name for x in humor_root_intent.children]:
        #     return

        # validate intent is leaf
        if len(intent.children) > 0:
            return

        for rfc in rr:
            rfc: RichFulfillmentContainer
            for rft in rfc:
                rft: RichFulfillmentText
                last_sentence: RichFulfillmentSentence = rft.sentences[-1]
                last_sentence.routine = self.get_routine(last_sentence)

        return rr

    def get_routine(self, rfs: RichFulfillmentSentence, routine_data=None):
        routine_data = routine_data if routine_data else self.config["routine_data"]
        return ";".join([routine_data.get("joy", ""), routine_data.get("cheeky", "")])


if __name__ == "__main__":
    title = "haru games rich response uploader"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    from hg_data import routine_data

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    config = {
        "credential": os.path.join(agents_dir, "haru-chat-games.json"),
        "routine_data": routine_data,
        "intents": {
            "madlibs": [],
            "trivia": [],
            "humor": [],
        },
    }

    rr_uploader = RichResponseUploader(config)
    rr_uploader.run()
