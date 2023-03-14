import sys
import os

sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}"))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../.."))
sys.path.append(os.path.abspath(f"{os.path.dirname(__file__)}/../../src"))


from hg_parser import HaruGamesParser
from hg_rr_uploader import HaruGamesRichResponseUploader


class HaruGamesUploader:
    def __init__(self, config) -> None:
        self.config = config

        self.parser = HaruGamesParser(config["parser"])
        self.uploader = HaruGamesRichResponseUploader(config["uploader"])

    def run(self):
        print("Parser is running...\t", end="")
        self.parser.run()
        print("done\n")

        print("Uploader is running...\t", end="")
        self.uploader.run(rich_responses=self.parser.parsed_data)
        print("done\n")

    def report(self):
        pass


if __name__ == "__main__":
    title = "haru chat uploader"
    version = "0.1.0"
    author = "Farhabi Helal"
    email = "farhabi.helal@jp.honda-ri.com"

    root_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../")
    agents_dir = os.path.abspath(os.path.join(root_dir, ".temp/keys"))
    exports_dir = os.path.abspath(os.path.join(root_dir, "exports"))

    from hg_data import routine_data

    config = {
        "parser": {
            "filepath": os.path.join(exports_dir, "Haru-Chat-Games(4).xlsx"),
        },
        "uploader": {
            "credential": os.path.join(agents_dir, "haru-chat-games.json"),
            "routine_data": routine_data,
        },
    }

    uploader = HaruGamesUploader(config)
    uploader.run()
    uploader.report()
