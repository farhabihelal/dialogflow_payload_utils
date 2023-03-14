from dataclasses import dataclass, field

from do.base_rich_dataclass import BaseRichDataClass

import xml.etree.ElementTree as ET


class BaseXMLDataClass(BaseRichDataClass):
    def toXmlString(self) -> str:
        pass


# <break type='4' time='0.6' />
# <usel genre='cheeky'>Ow, I see.</usel>


@dataclass
class SSMLTag(BaseXMLDataClass):
    key: str
    value: str
    attributes: dict

    def toXmlString(self) -> str:
        xml = f"<{self.key}"
        for attr_key, attr_val in self.attributes.items():
            xml += f" {attr_key}='{attr_val}'"
        xml += "/>" if self.key == "break" else f"/>{self.value}</{self.key}>"
        return xml

    def __repr__(self) -> str:
        return self.toXmlString()

    @classmethod
    def from_text(self, text: str):
        return


@dataclass
class SSMLText:
    text: str = ""
    tags: list = field(default_factory=list)

    @classmethod
    def from_text(self, text: str):
        ssml_text = SSMLText()
        tree = ET.ElementTree(ET.fromstring("<root>" + text + "</root>"))
        tags = []
        i = 0
        while i < len(text):
            if text[i] == "<" and ((i + 1) < len(text) and text[i + 1] != "/"):
                j = i + 1
                while j < len(text):
                    if text[j] == " ":
                        tag = text[i + 1 : j]
                        tags.append(tag)
                        i = j
                        break
                    j += 1
            i += 1

        for tag in tags:
            elem = tree.find(f".//{tag}")
            attrs = elem.attrib
            value = elem.text.strip() if elem.text else ""
            ssml_tag = SSMLTag(key=tag, value=value, attributes=attrs)

        return ssml_text


class SSML:
    TAG_LIST = [
        "break",
        "genre",
    ]

    def __init__(self, config: dict) -> None:
        self.configure(config)

    def configure(self, config: dict):
        self.config = config


if __name__ == "__main__":
    dc = SSMLTag(key="break", value="", attributes={"type": "4", "time": "0.6"})
    print(dc)

    ssml_text = SSMLText.from_text(
        text="Hey there. <usel genre='highnrg'>I am so excited!</usel> My name is Haru. <break type='4' time='1.0'/> How are you?"
    )
