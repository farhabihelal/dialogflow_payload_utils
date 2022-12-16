import sys
import os


def verify_file_sanity(filepath: str) -> bool:
    return os.path.exists(filepath) and os.path.isfile(filepath)


def get_filename(filepath: str):
    if verify_file_sanity(filepath):
        return os.path.splitext(os.path.basename(filepath))[0]
