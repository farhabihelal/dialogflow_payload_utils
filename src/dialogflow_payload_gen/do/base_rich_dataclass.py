from dataclasses import asdict, dataclass

import re


@dataclass
class BaseRichDataClass:
    @classmethod
    def fromDict(self, obj: dict):
        return self(**obj)

    def toDict(self):
        return asdict(self)

    def tolist(self):
        return list(self.toDict().values())

    @classmethod
    def all_fields(self):
        return [x for x in self.__dataclass_fields__]

    def __repr__(self) -> str:
        return str(self.toDict())

    def __eq__(self, obj) -> bool:
        if type(self) == type(obj):
            return self.toDict() == obj.toDict()
        return False

    def __post_init__(self):
        for k in self.all_fields():
            v = getattr(self, k)
            if type(v) == str:
                v = v.strip()
                v = re.sub("\s{2,}", " ", v)
                v = re.sub('["]', "", v)
                setattr(self, k, v)


if __name__ == "__main__":
    dc = BaseRichDataClass()
