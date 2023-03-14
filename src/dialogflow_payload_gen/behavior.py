import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from nlp import NLP

from do.base_datarow import DataRow


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

    @classmethod
    def get_default_profile(self):
        profile = {
            "genre_map": Behavior.DEFAULT_GENRE_MAP,
            "routine_map": Behavior.DEFAULT_ROUTINE_MAP,
            "override": False,
            "override_intent_names": [],
        }
        return profile

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

    def get_genre(self, emotion: str, genre_map=None) -> str:
        genre_map = genre_map if genre_map else Behavior.DEFAULT_GENRE_MAP
        return genre_map.get(emotion, "default")

    def get_genre_from_text(self, text: str, genre_map=None) -> str:
        genre_map = genre_map if genre_map else Behavior.DEFAULT_GENRE_MAP
        return (
            genre_map["question"]
            if self.nlp.is_question(text)
            else self.get_genre(
                emotion=self.nlp.classify_emotion(text)["label"], genre_map=genre_map
            )
        )

    def get_emotion(self, text: str) -> dict:
        return self.nlp.classify_emotion(text)

    def get_routine(self, genre: str, routine_map: dict = None) -> str:
        routine_map = routine_map if routine_map else Behavior.DEFAULT_ROUTINE_MAP
        return routine_map.get(genre, Behavior.DEFAULT_ROUTINE_MAP["default"])

    def add_behavior(
        self, datarow: DataRow, profile: dict = None, override_behavior: bool = False
    ) -> DataRow:
        """
        Adds behavior annotations to DataRow.

        Args:
            datarow (DataRow): source object
            profile (dict, optional): Behavior profile to use. If no profile is given, default will be used. Defaults to None.
            override_behavior (bool): Determines whether to override existing annotation or not. Annotations will be added where the value is empty even if set to False. Defaults to False.

        Returns:
            DataRow: modified object
        """

        # loads profile if available otherwise uses default
        profile = profile if profile else self.config.get("behavior_profile")
        profile = profile if profile else Behavior.get_default_profile()

        auto_emotion = self.get_emotion(datarow.text)

        datarow.auto_emotion = (
            auto_emotion["label"]
            if override_behavior or not datarow.auto_emotion
            else datarow.auto_emotion
        )
        datarow.auto_score = (
            auto_emotion["score"]
            if override_behavior or not datarow.auto_score
            else datarow.auto_score
        )

        datarow.auto_genre = (
            self.get_genre_from_text(text=datarow.text, genre_map=profile["genre_map"])
            if override_behavior or not datarow.auto_genre
            else datarow.auto_genre
        )

        datarow.genre = (
            datarow.auto_genre
            if override_behavior or not datarow.genre
            else datarow.genre
        )

        datarow.routine_id = (
            self.get_routine(datarow.genre, routine_map=profile["routine_map"])
            if override_behavior or not datarow.routine_id
            else datarow.routine_id
        )

        return datarow

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except AttributeError as e:
            return self.config[__name]


if __name__ == "__main__":
    config = {
        "parsed_data": None,
        "emotion_model_name": "",
        "override_behavior": False,
        "override_intent_names": [],
        "behavior_profile": {
            "routine_map": {},
            "genre_map": {},
        },
    }

    mapper = Behavior(config)
    # mapper.run(parsed_data=None, routine_map=None)

    datarow = DataRow(text="Hello there!")
    profile = None
    new_datarow = mapper.add_behavior(
        datarow=datarow, profile=profile, override_behavior=False
    )
    print(new_datarow)
