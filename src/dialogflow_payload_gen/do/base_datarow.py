import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dataclasses import dataclass

from base_rich_dataclass import BaseRichDataClass


@dataclass
class DataRow(BaseRichDataClass):
    topic: str = ""
    intent: str = ""
    response: str = ""
    paraphrase: str = ""
    sentence: str = ""
    text: str = ""
    genre: str = ""
    emotion: str = ""
    auto_genre: str = ""
    auto_emotion: str = ""
    auto_score: str = ""
    routine: str = ""
    routine_id: str = ""
    comments: str = ""
