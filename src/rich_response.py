from dataclasses import asdict, dataclass, field


@dataclass
class BaseRichDataClass:
    @classmethod
    def fromDict(self, obj: dict):
        return self(**obj)

    def toDict(self):
        return asdict(self)


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
