import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


import pandas as pd

from do.rich_response import (
    RichFulfillmentSentence,
    RichFulfillmentText,
    RichFulfillmentMessageCollection,
    RichFulfillmentContainer,
)

from do.base_datarow import DataRow

from dialogflow_payload_gen.behavior import Behavior

from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, config: dict) -> None:
        self._config = config
        self._data = None
        self._header = []
        self._header_map = {}

        self.unique_intents: dict = {}
        self.intent_names: list = []

        self.parsed_data = None

        self._behavior = Behavior(config.get("behavior", {}))

    @abstractmethod
    def load(self, filepath=None):
        raise NotImplementedError()

    def run(self, filepath=None):
        self.load(filepath)
        self.parse()

    def parse(self):
        parsed_data = {}

        for intent in self.intent_names:
            parsed_data[intent] = []
            intent_rows = self.get_intent_rows(intent)
            responses = self.get_responses(intent_rows)

            rich_responses = RichFulfillmentMessageCollection()
            for i, response in enumerate(responses):
                rich_response = RichFulfillmentContainer()
                paraphrases = self.get_paraphrases(response)
                sentences = []
                for j, paraphrase in enumerate(paraphrases):
                    sentences = self.get_sentences_with_metadata(paraphrase)
                    # print(f"Intent\t\t: {intent}")
                    # print(f"Response\t: {i}")
                    # print(f"Paraphrase\t: {j}")
                    # print(f"Sentences")
                    # for k, sent in enumerate(sentences):
                    #     print(f"{k}\t\t: {sent['text']}")
                    # print("\n\n")

                    rich_text = RichFulfillmentText(
                        sentences=sentences,
                        text=" ".join([x.text for x in sentences]),
                    )
                    rich_response.append(rich_text)
                rich_responses.append(rich_response)

            parsed_data[intent] = rich_responses

        self.parsed_data = parsed_data

    def get_intent_rows(self, intent: str, start_idx=0) -> list:
        intents = []
        for i in range(start_idx, len(self._data)):
            if self._data[i][self._header_map["intent"]] == intent:
                intents.append(self._data[i])

        return intents

    def get_unique_intents(self) -> dict:
        intents = {}

        for data in self._data:
            intent = data[self._header_map["intent"]]
            if not intents.get(intent):
                intents[intent] = 0

            intents[intent] += 1

        return intents

    def get_responses(self, intents: list) -> list:
        responses = {}
        cur_idx = 1

        response = []
        for intent in intents:
            response_idx = intent[self._header_map["response"]]

            if response_idx != cur_idx:
                responses[cur_idx] = response
                response = []
                cur_idx = response_idx

            response.append(intent)

        responses[cur_idx] = response

        return list(responses.values())

    def get_paraphrases(self, responses: list) -> list:
        """
        returns a list of paraphrases for a single response block.

        @param
        paraphrases : list of rows with the same response id

        @returns
        list of paraphrases
        """
        paraphrases = {}
        cur_idx = 1

        sentences = []
        for response in responses:
            paraphrase_idx = response[self._header_map["paraphrase"]]

            if paraphrase_idx != cur_idx:
                paraphrases[cur_idx] = sentences
                sentences = []
                cur_idx = paraphrase_idx

            sentences.append(response)

        paraphrases[cur_idx] = sentences

        return list(paraphrases.values())

    def get_sentences(self, paraphrases: list) -> list:
        """
        returns the sentences for a single paraphrase.

        @param
        paraphrases : list of rows with the same paraphrase id

        @returns
        list of sentences for the paraphrase
        """
        return [x[self._header_map["text"]] for x in paraphrases]

    def get_sentences_with_metadata(self, paraphrases: list) -> list:
        """
        returns the sentences for a single paraphrase.

        @param
        paraphrases : list of rows with the same paraphrase id

        @returns
        list of sentence objects for the paraphrase
        """
        return [self.dr_to_rfs(x) for x in self.get_datarows(paraphrases)]

    def get_datarows(self, paraphrases: list) -> list:
        """
        returns datarows for corresponding sentences of a single paraphrase.

        @param
        paraphrases : list of rows with the same paraphrase id

        @returns
        list of datarow objects for the paraphrase
        """
        return [self.get_datarow(x) for x in paraphrases]

    def get_datarow(self, data: list):
        return self._behavior.add_behavior(
            datarow=DataRow.fromDict(
                {k: data[self._header_map[k]] for k in DataRow.all_fields()}
            ),
            profile=self._config.get("behavior_profile"),
            override_behavior=False,
        )

    # ORIGINAL
    # def dr_to_rfs(self, dr: DataRow):
    #     """
    #     Converts DataRow to Rich Fulfillment Sentence.
    #     """
    #     return RichFulfillmentSentence.fromDict(
    #         {
    #             k: v
    #             for k, v in dr.toDict().items()
    #             if k in RichFulfillmentSentence.all_fields()
    #         }
    #     )

    # QUICK FIX
    def dr_to_rfs(self, dr: DataRow):
        """
        Converts DataRow to Rich Fulfillment Sentence.
        """
        rfs = RichFulfillmentSentence.fromDict(
            {
                k: v
                for k, v in dr.toDict().items()
                if k in RichFulfillmentSentence.all_fields()
            }
        )

        rfs.routine = str(
            int(dr.routine_id) if type(dr.routine_id) == float else dr.routine_id
        )

        return rfs


if __name__ == "__main__":
    title = "base parser"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    import argparse

    default_config = {
        "filepath": "",
    }

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--filepath",
        dest="filepath",
        default=default_config.get("filepath", ""),
        required=True,
        type=str,
        help="Path to the  file to parse.",
    )
    args, args_list = parser.parse_known_args()

    config = {
        "filepath": args.filepath,
        "behavior": {
            "override_behavior": False,
            "override_intent_names": [],
            "profile": {},
        },
    }

    parser = Parser(config)
    parser.run()
    data = parser.parsed_data
    print(data)
