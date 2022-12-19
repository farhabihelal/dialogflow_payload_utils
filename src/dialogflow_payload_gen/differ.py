import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import difflib

from dataclasses import dataclass, field


@dataclass
class DiffResult:
    additions: list = field(default_factory=list)
    deletions: list = field(default_factory=list)
    modifications: list = field(default_factory=list)


class Differ:
    def __init__(self, config: dict) -> None:
        self.config = config

        self.ref_data = None
        self.compare_data = None

        self.diff_data = None
        self.diff_result = None

    def run(self, ref_data: list = None, compare_data: list = None):
        ref_data = ref_data if ref_data else self.config["ref_data"]
        compare_data = compare_data if compare_data else self.config["compare_data"]

        self.ref_data = ref_data
        self.compare_data = compare_data

        diff_data = list(difflib.unified_diff(a=ref_data, b=compare_data, n=0))
        self.diff_data = diff_data

        diff_result = self.process_diff_data(diff_data=diff_data)
        self.diff_result = diff_result

    def preprocess_diff_data(self, diff_data: list = None):
        processed_diff_data = [
            line for line in diff_data if not line.startswith(("+++", "---", "@@"))
        ]

        return processed_diff_data

    def process_diff_data(self, diff_data: list = None) -> DiffResult:
        processed_diff_data = self.preprocess_diff_data(diff_data)

        diff_result = DiffResult()

        i = 0
        while i < len(processed_diff_data):
            line: str = processed_diff_data[i]
            next_line: str = (
                processed_diff_data[i + 1] if i < len(processed_diff_data) - 1 else None
            )

            if line.startswith("+"):
                if next_line:
                    # addition
                    diff_result.additions.append(line[1:])

            elif line.startswith("-"):
                if next_line and next_line.startswith("+"):
                    # modification
                    data = {"ref": line[1:], "current": next_line[1:]}
                    diff_result.modifications.append(data)
                    i += 1
                else:
                    # deletion
                    diff_result.deletions.append(line[1:])
            i += 1

        return diff_result

    def report(self):
        pass


if __name__ == "__main__":

    ref_data = [
        ["topic-a", "intent-a", "abcd"],
        ["topic-a", "intent-b", "abcd"],
        ["topic-a", "intent-c", "abcd"],
        ["topic-a", "intent-d", "abcd"],
        ["topic-a", "intent-e", "abcd"],
        ["topic-a", "intent-f", "abcd"],
        ["topic-a", "intent-g", "abcd"],
    ]
    compare_data = [
        ["topic-aa", "intent-a", "abcd"],
    ]

    config = {
        "ref_data": [",".join(x) for x in ref_data],
        "compare_data": [",".join(x) for x in compare_data],
    }

    diff = Differ(config)
    diff.run()
    diff.report()
