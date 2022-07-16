from pprint import pformat
from typing import Dict, List
from rich_text import RichText


def guess_property_type(res: Dict):
    _PROPERTY_TYPES_ = {
        "property_item": PropertyItem,
        "title": TitleProperty,
        "rich_text": RichTextProperty,
        "number": NumberProperty,
        "select": SelectProperty,
        "multi_select": TagsProperty,
    }
    property_type = res["type"]
    if property_type in _PROPERTY_TYPES_:
        return _PROPERTY_TYPES_[property_type]
    else:
        return BaseProperty


class BaseProperty:
    def __init__(self, res: Dict):
        self.res = res


class PropertyItem(BaseProperty):
    def __init__(self, res: Dict):
        super().__init__(res)
        self.subs = []
        for sub in res["results"]:
            property_type = guess_property_type(sub)
            self.subs.append(property_type(sub))

    def __getitem__(self, item):
        return self.subs[item]

    def __len__(self):
        return len(self.subs)

    def __repr__(self):
        return "PropertyItem(" + pformat([i.__repr__() for i in self.subs]) + ")"


class TitleProperty(BaseProperty):
    def __init__(self, res: Dict):
        super().__init__(res)

    @staticmethod
    def template(**kwargs):
        """
        :param kwargs:
            text: str, required
            bold: bool, default False
            italic: bool, default False
            strikethrough: bool, default False
            underline: bool, default False
            code: bool, default False
            color: str, default "default"
        :return: dict
        """
        data = {
            "title": RichText().set_plain_text(**kwargs).res
        }
        return data

    @property
    def plain_text(self):
        return RichText([self.res["title"]]).plain_text

    def __repr__(self):
        return "TitleProperty(" + pformat({"plain_text": self.plain_text}) + ")"


class RichTextProperty(BaseProperty):
    def __init__(self, res: Dict):
        super().__init__(res)

    @staticmethod
    def template(**kwargs):
        data = {
            "rich_text": RichText().set_plain_text(**kwargs).res
        }
        return data

    @property
    def plain_text(self):
        return RichText([self.res["rich_text"]]).plain_text

    def __repr__(self):
        return "RichTextProperty(" + pformat({"plain_text": self.plain_text}) + ")"


class NumberProperty(BaseProperty):
    def __init__(self, res: Dict):
        super().__init__(res)

    @staticmethod
    def template(number):
        data = {
            "number": number
        }
        return data

    @property
    def value(self):
        return self.res["number"]

    def __repr__(self):
        return "NumberProperty(" + pformat({"value": self.value}) + ")"


class SelectProperty(BaseProperty):
    def __init__(self, res: Dict):
        super().__init__(res)

    @staticmethod
    def template(name: str):
        data = {
            "select": {
                "name": name
            }
        }
        return data

    @property
    def select(self):
        if self.res["select"]:
            return self.res["select"]["name"]
        return None

    def __repr__(self):
        return "SelectProperty(" + pformat({"select": self.select}) + ")"


class TagsProperty(BaseProperty):
    def __init__(self, res: Dict):
        super().__init__(res)

    @staticmethod
    def template(tags: List[str]):
        data = {
            "multi_select": [{"name": tag} for tag in tags]
        }
        return data

    @property
    def tag(self):
        if self.res["multi_select"]:
            return [obj["name"] for obj in self.res["multi_select"]]
        return []

    def __repr__(self):
        return "TagProperty(" + pformat({"tag": self.tag}) + ")"
