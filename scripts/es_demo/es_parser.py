import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../.."))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))


from dialogflow_payload_gen.parser_xl import ParserXL

import re
import pandas as pd


class ESParser(ParserXL):
    def __init__(self, config) -> None:
        super().__init__(config)

    def load(self, filepath=None):
        filepath = filepath if filepath else self._config["filepath"]

        self._data = []
        self._xl_sheets = {}

        self._xl = pd.ExcelFile(filepath)

        for sheet in self._xl.sheet_names:
            if not re.match("day\-\d\-session\-\d", sheet):
                continue

            df = pd.read_excel(self._xl, sheet_name=sheet)
            self._xl_sheets[sheet] = df
            df.fillna("", inplace=True)

            self._headers[sheet] = df.columns.values.tolist()
            self._data.extend(df.values.tolist())
            self._data_sheets[sheet] = df.values.tolist()

        self._header = next(iter(self._headers.values()))
        self._header_map = {header: i for i, header in enumerate(self._header)}
        self.unique_intents = self.get_unique_intents()
        self.intent_names = list(self.unique_intents.keys())


if __name__ == "__main__":
    title = "es parser"
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
        # required=True,
        type=str,
        help="Path to the  file to parse.",
    )
    args, args_list = parser.parse_known_args()

    # config = {
    #     "filepath": args.filepath,
    #     "session_data": session_data,
    # }

    from es_data import session_data

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/..")

    config = {
        "filepath": os.path.join(root_dir, "exports", "ES.xlsx"),
        "session_data": session_data,
    }

    parser = ESParser(config)
    parser.run()
    print(parser.parsed_data)
