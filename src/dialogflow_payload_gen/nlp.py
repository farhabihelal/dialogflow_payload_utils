import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import re

from transformers import pipeline
import spacy


class NLP:
    DEFAULT_EMOTION_MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"

    DEFAULT_EMOTION_LIST = [
        "neutral",
        "anger",
        "disgust",
        "fear",
        "joy",
        "sadness",
        "surprise",
    ]

    def __init__(self, config: dict) -> None:
        self.configure(config)

        self.emotion_model_name = (
            self.emotion_model_name
            if self.emotion_model_name
            else NLP.DEFAULT_EMOTION_MODEL_NAME
        )

        self.emotion_model = pipeline(
            "sentiment-analysis", model=self.emotion_model_name, top_k=None
        )

        self.nlp = spacy.load("en_core_web_md")

        self.valid_chars = "\w\s</>?;.,\"':\-$@#%&"
        self.invalid_pattern = re.compile(f"[^{self.valid_chars}]")

    def configure(self, config: dict):
        self.config = config
        self.emotion_model_name = self.config.get("emotion_model_name")

    def is_question(self, sentence: str) -> bool:
        return sentence.endswith("?")

    def get_sentences(self, text: str) -> list:
        result = self.nlp(text)
        return [x.text for x in result.sents]

    def clean_text(self, text: str) -> str:
        text = self.invalid_pattern.sub("", text)
        text = re.sub("\s+", " ", text)
        return text.strip()

    def classify_emotion(self, text: str) -> dict:
        raw_data = self.emotion_model(text)
        best_emotion = max(raw_data[0], key=lambda x: x["score"])
        return best_emotion


if __name__ == "__main__":
    config = {
        "emotion_model_name": "",
    }
    nlp = NLP(config)
    # print(nlp.get_sentences("Hello there. My name is Haru."))

    text = nlp.clean_text("abcABC123!@#$%^&*()...    _-+=?,.</>;'\"[]\{\}|\\")
    print(text)
