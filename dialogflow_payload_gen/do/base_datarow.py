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
    emotion: str = ""
    genre: str = ""
    routine: str = ""
    routine_id: str = ""
    comments: str = ""
