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

    def __post_init__(self):
        for field in self.all_fields():
            setattr(
                self,
                field,
                str(
                    int(getattr(self, field))
                    if type(getattr(self, field)) == float and "score" not in field
                    else getattr(self, field)
                ),
            )

    def __eq__(self, obj) -> bool:
        return (
            self.topic == obj.topic
            and self.intent == obj.intent
            and self.response == obj.response
            and self.paraphrase == obj.paraphrase
            and self.sentence == obj.sentence
            and self.text == obj.text
        )
