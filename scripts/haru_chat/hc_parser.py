import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../.."))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))


from dialogflow_payload_gen.parser_xl import ParserXL


class HCParser(ParserXL):
    def __init__(self, config) -> None:
        super().__init__(config)


if __name__ == "__main__":

    title = "haru chat parser"
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

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/..")

    config = {
        "filepath": os.path.join(root_dir, "exports", "Haru-Chat.xlsx"),
    }

    parser = HCParser(config)
    parser.run()
    print(parser.parsed_data)
