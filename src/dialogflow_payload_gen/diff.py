import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import difflib

from parser_xl import ParserXL

from utils import verify_file_sanity, get_filename


class Diff:
    def __init__(self, config: dict) -> None:
        self.config = config

        self.data = {}
        self.ref_parser = None
        self.comp_parsers = {}

        self.ref_data = None
        self.comp_data = {}

    def run(self, ref_filepath: str = None, compare_filepaths: list = None):

        self.load(ref_filepath=ref_filepath, compare_filepaths=compare_filepaths)

        diff_data = self.compare(
            ref_parser=self.ref_parser, comp_parsers=self.comp_parsers
        )

    def load(self, ref_filepath: str = None, compare_filepaths: list = None):

        ref_filepath = ref_filepath if ref_filepath else self.config["ref_filepath"]

        compare_filepaths = (
            compare_filepaths if compare_filepaths else self.config["compare_filepaths"]
        )

        self.ref_parser = self.get_ref_parser(ref_filepath)
        self.ref_parser.load()

        self.compare_parsers = self.get_compare_parsers(compare_filepaths)

        for filename, parser in self.comp_parsers.items():
            parser: ParserXL
            parser.load()

    def get_ref_parser(self, ref_filepath: str = None):
        ref_filepath = ref_filepath if ref_filepath else self.config["ref_filepath"]

        return self.get_parser(ref_filepath)

    def get_compare_parsers(self, compare_filepaths: list = None) -> dict:
        return {
            get_filename(filepath): self.get_parser(filepath)
            for filepath in compare_filepaths
        }

    def get_parser(self, filepath: str):
        if not verify_file_sanity(filepath):
            raise ValueError("")

        return ParserXL(
            {
                "filepath": filepath,
            }
        )

    def compare_data(self, ref_parser: ParserXL, comp_parser: ParserXL):
        ref_data_sheets = ref_parser._data_sheets
        comp_data_sheets = comp_parser._data_sheets

        diff_sheet_data = {}

        for sheet_name, ref_data in ref_data_sheets:
            comp_data = comp_data_sheets.get(sheet_name)
            if not comp_data:
                diff_sheet_data[sheet_name] = ref_data

        diff = self.get_diff(ref_data, comp_data)

        return diff

    def compare(self, ref_parser=None, comp_parsers: dict = None):

        diff_data = {}

        for filename, comp_parser in comp_parsers.items():
            diff = self.compare_data(ref_parser=ref_parser, comp_parser=comp_parser)
            diff_data[filename] = diff

        return diff_data

    def get_diff(self, ref_data: list, comp_data: list):

        return [list(set(ref_data) - set(comp_data) | set(comp_data) - set(ref_data))]

    def report(self):
        pass


if __name__ == "__main__":

    export_dir = os.path.abspath(f"{os.path.dirname(__file__)}/../../exports")

    config = {
        "ref_filepath": os.path.join(export_dir, "ES_v4.xlsx"),
        "compare_filepaths": [
            os.path.join(export_dir, "ES_v5.xlsx"),
        ],
    }

    diff = Diff(config)
    diff.run()
    diff.report()
