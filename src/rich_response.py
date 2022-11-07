from dataclasses import asdict, dataclass, field


@dataclass
class BaseRichDataClass:
    @classmethod
    def fromDict(self, obj: dict):
        return self(**obj)

    def toDict(self):
        return asdict(self)

    def __repr__(self) -> str:
        return str(self.toDict())


@dataclass
class RichFulfillmentSentence(BaseRichDataClass):
    """
    Single sentence of a fulfillment text.
    """

    text: str = ""
    alt_text: str = ""
    genre: str = "neutral"
    emotion: str = ""
    ssml_text: str = ""
    alt_ssml_text: str = ""
    routine: dict = field(default_factory=dict)
    silence: dict = field(default_factory=dict)

    def toDict(self):
        self.ssml_text = f'<usel genre="{self.genre}">{self.text}</usel>'
        return super().toDict()


@dataclass
class RichFulfillmentText(BaseRichDataClass):
    """
    Single fulfillment text that may contain several sentences.
    """

    sentences: list = field(default_factory=list)
    text: str = ""
    alt_text: str = ""
    priority: int = 10


class RichFulfillmentContainer(list):
    """
    Container of multiple fulfillment texts.
    """

    def __init__(self, fulfillment_texts: list = []) -> None:
        """ """
        list.__init__(self)

    def __repr__(self) -> str:
        return "\n".join([repr(x) for x in self])


class RichFulfillmentMessageCollection(list):
    """
    Contains multiple fulfillment containers.
    """

    def __init__(self, containers: list = []):
        list.__init__(self)

        for container in containers:
            rr_container = container

            if type(container) != RichFulfillmentContainer:
                rr_container = RichFulfillmentContainer()
                for response in container:
                    rft = RichFulfillmentText.fromDict(response)
                    rft.sentences = [
                        RichFulfillmentSentence.fromDict(x)
                        for x in response["sentences"]
                    ]
                    rr_container.append(rft)
            self.append(rr_container)

    @staticmethod
    def from_payload(payload: dict):
        responses = payload.get("messages", [])

        rfm_collection = RichFulfillmentMessageCollection()
        for container in responses:
            rt_container = RichFulfillmentContainer()
            for response in container:
                rr = RichFulfillmentText(
                    text=response["text"],
                    sentences=[
                        RichFulfillmentSentence.fromDict(x)
                        for x in response["sentences"]
                    ],
                )
                rt_container.append(rr)
            rfm_collection.append(rt_container)

        return rfm_collection

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self) -> str:
        return "\n".join([repr(x) for x in self])


if __name__ == "__main__":

    payload = {
        "messages": [
            [
                {
                    "text": "Are you going somewhere, $user_name?",
                    "sentences": [
                        {
                            "ssml_text": '<usel genre="neutral">Are you going somewhere, $user_name?</usel>',
                            "silence": {},
                            "text": "Are you going somewhere, $user_name?",
                            "alt_text": "",
                            "genre": "neutral",
                            "emotion": "",
                            "routine": {},
                            "alt_ssml_text": "",
                        }
                    ],
                },
                {
                    "sentences": [
                        {
                            "genre": "neutral",
                            "emotion": "",
                            "ssml_text": '<usel genre="neutral">Are you going to leave home soon, $user_name?</usel>',
                            "silence": {},
                            "alt_ssml_text": "",
                            "text": "Are you going to leave home soon, $user_name?",
                            "routine": {},
                            "alt_text": "",
                        }
                    ],
                    "text": "Are you going to leave home soon, $user_name?",
                },
                {
                    "text": "$user_name, are you going somewhere?",
                    "sentences": [
                        {
                            "alt_ssml_text": "",
                            "text": "$user_name, are you going somewhere?",
                            "routine": {},
                            "alt_text": "",
                            "ssml_text": '<usel genre="neutral">$user_name, are you going somewhere?</usel>',
                            "silence": {},
                            "genre": "neutral",
                            "emotion": "",
                        }
                    ],
                },
                {
                    "text": "Pardon me $user_name, but it seems to me that you are preparing to leave. Is that correct?",
                    "sentences": [
                        {
                            "emotion": "",
                            "genre": "neutral",
                            "alt_text": "",
                            "ssml_text": '<usel genre="neutral">Pardon me $user_name, but it seems to me that you are preparing to leave.</usel>',
                            "text": "Pardon me $user_name, but it seems to me that you are preparing to leave.",
                            "routine": {},
                            "silence": {},
                            "alt_ssml_text": "",
                        },
                        {
                            "silence": {},
                            "ssml_text": '<usel genre="neutral">Is that correct?</usel>',
                            "alt_ssml_text": "",
                            "genre": "neutral",
                            "text": "Is that correct?",
                            "alt_text": "",
                            "routine": {},
                            "emotion": "",
                        },
                    ],
                },
                {
                    "text": "Pardon me $user_name, but it seems you are about to leave. Am I correct?",
                    "sentences": [
                        {
                            "genre": "neutral",
                            "alt_ssml_text": "",
                            "alt_text": "",
                            "ssml_text": '<usel genre="neutral">Pardon me $user_name, but it seems you are about to leave.</usel>',
                            "silence": {},
                            "emotion": "",
                            "text": "Pardon me $user_name, but it seems you are about to leave.",
                            "routine": {},
                        },
                        {
                            "ssml_text": '<usel genre="neutral">Am I correct?</usel>',
                            "alt_text": "",
                            "silence": {},
                            "routine": {},
                            "emotion": "",
                            "genre": "neutral",
                            "alt_ssml_text": "",
                            "text": "Am I correct?",
                        },
                    ],
                },
            ]
        ]
    }

    rfm_collection = RichFulfillmentMessageCollection.from_payload(payload)
    print(repr(rfm_collection))
    print(hash(rfm_collection))
