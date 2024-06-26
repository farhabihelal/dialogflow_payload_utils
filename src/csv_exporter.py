import pandas as pd

from rich_response import RichFulfillmentSentence, RichFulfillmentText


class Sentence:
    pass


class TextResponse:
    pass


class Response:
    pass


class CSVExporter:
    def __init__(self, config) -> None:

        self._config = config
        self._csv = None
        self._data = None
        self._header = []
        self._header_map = {}

        self.unique_intents: dict = {}
        self.intent_names: list = []

        self.parsed_data = None

        self.load()

    def load(self):
        self._csv = pd.read_csv(self._config["csv_filepath"], sep="\t", header=0)
        self._data = self._csv.values.tolist()
        self._header = self._csv.columns.values.tolist()
        self._header_map = {header: i for i, header in enumerate(self._header)}
        self.unique_intents = self.get_unique_intents()
        self.intent_names = list(self.unique_intents.keys())

    def run(self):
        self.parse()

    def parse(self):
        parsed_data = {}

        for intent in self.intent_names:
            parsed_data[intent] = []
            intent_rows = self.get_intent_rows(intent)
            responses = self.get_responses(intent_rows)

            rich_responses = []
            rich_resonse = []
            for i, response in enumerate(responses):
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
                        sentences=[
                            RichFulfillmentSentence.fromDict(x) for x in sentences
                        ],
                        text=" ".join([x["text"] for x in sentences]),
                    )
                    rich_resonse.append(rich_text)
                rich_responses.append(rich_resonse)

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
        return [
            {k: x[self._header_map[k]] for k in ["text", "emotion", "genre"]}
            for x in paraphrases
        ]


if __name__ == "__main__":

    title = "csv parser"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    import argparse

    default_config = {
        "csv_filepath": "",
    }

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--csv_filepath",
        dest="csv_filepath",
        default=default_config.get("csv_filepath", ""),
        # required=True,
        type=str,
        help="Path to the CSV file to parse.",
    )
    args, args_list = parser.parse_known_args()

    config = {
        "csv_filepath": args.csv_filepath,
    }

    parser = CSVParser(config)
    parser.run()
