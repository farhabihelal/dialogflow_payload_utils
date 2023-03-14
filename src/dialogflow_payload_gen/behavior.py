import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from nlp import NLP


class Behavior:
    GENRE_LIST = [
        "default",
        "cheeky",
        "conv",
        "convspon",
        "empathetic",
        "highnrg",
        "sad",
        "serious",
        "smile",
        "question",
        "whiny",
        "whisper-yell",
    ]

    DEFAULT_GENRE_MAP = {
        "anger": "serious",
        "disgust": "whiny",
        "fear": "serious",
        "joy": "highnrg",
        "neutral": "default",
        "question": "question",
        "sadness": "sad",
        "surprise": "highnrg",
    }

    DEFAULT_ROUTINE_MAP = {
        "default": "",
        "cheeky": "",
        "conv": "",
        "convspon": "",
        "empathetic": "",
        "highnrg": "",
        "sad": "",
        "serious": "",
        "smile": "",
        "question": "",
        "whiny": "",
        "whisper-yell": "",
    }

    def __init__(self, config: dict) -> None:
        self.configure(config)
        self.nlp = NLP(config)

    def configure(self, config: dict):
        self.config = config

    def run(self, parsed_data=None, routine_map=None):
        parsed_data = parsed_data if parsed_data else self.config["parsed_data"]
        routine_map = routine_map if routine_map else self.config["routine_map"]

        for intent_name in parsed_data:
            rr = parsed_data[intent_name]

    def get_genre(self, emotion: dict, genre_map=None) -> str:
        genre_map = genre_map if genre_map else Behavior.DEFAULT_GENRE_MAP
        return genre_map.get(emotion["label"], "default")

    def get_genre_from_text(self, text: str, genre_map=None) -> str:
        return self.get_genre(
            emotion=self.nlp.classify_emotion(text), genre_map=genre_map
        )

    def get_emotion(self, text: str) -> dict:
        return self.nlp.classify_emotion(text)

    def get_routine(self, genre: str, routine_map: dict = None) -> str:
        routine_map = routine_map if routine_map else Behavior.DEFAULT_ROUTINE_MAP
        return routine_map.get(genre, Behavior.DEFAULT_ROUTINE_MAP["default"])

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except AttributeError as e:
            return self.config[__name]


if __name__ == "__main__":
    config = {
        "routine_map": {
            "highnrg": [],
            "cheeky": [],
            "sad": [],
            "joy": [],
            "neutral": [],
        },
        "genre_map": {},
        "parsed_data": None,
        "emotion_model_name": "",
    }

    mapper = Behavior(config)
    # mapper.run(parsed_data=None, routine_map=None)

    print(mapper.get_genre_from_text(""))
