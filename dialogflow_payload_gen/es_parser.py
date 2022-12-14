import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


import pandas as pd


from csv_parser_xl import CSVParserXL


class ESParser(CSVParserXL):
    def __init__(self, config) -> None:

        super().__init__(config)


if __name__ == "__main__":

    title = "csv parser"
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
        help="Path to the CSV file to parse.",
    )
    args, args_list = parser.parse_known_args()

    # config = {
    #     "filepath": args.filepath,
    #     "session_data": session_data,
    # }

    session_data = {
        "1": {
            "1": [
                "topic-intro",
                "topic-day-one-session-one-names-origins",
                "topic-day-one-session-one-transition-age",
                "topic-day-one-session-one-age",
            ],
            "2": [
                "topic-day-one-session-two-intro",
                "topic-travel-homecountry",
                "topic-day-one-session-two-transition",
                "topic-hometown",
                "topic-day-one-session-two-outro",
            ],
        },
        "2": {
            "1": [
                "topic-day-two-session-one-intro",
                "topic-day-two-family",
                "topic-day-two-session-one-transition",
                "topic-day-two-parents",
                "topic-day-two-session-one-outro",
            ],
            "2": [
                "topic-day-two-session-two-intro",
                "topic-pet-new",
                "topic-day-two-session-two-transition",
                "topic-lemurs",
                "topic-day-two-session-two-end",
            ],
        },
    }

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/..")

    config = {
        "filepath": os.path.join(root_dir, "exports", "ES.xlsx"),
        "session_data": session_data,
    }

    parser = ESParser(config)
    parser.run()
    print(parser.parsed_data)
