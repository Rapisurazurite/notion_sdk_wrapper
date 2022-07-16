from typing import List


class RichText:
    def __init__(self, res: List = []):
        self.available_styles = ["text", "mention", "equation"]
        if res is None:
            res = []
        self._res = res

    def update(self, res: List):
        self._res = res

    @property
    def plain_text(self):
        _plain_text = [c["plain_text"] for c in self._res]
        return "".join(_plain_text)

    def set_plain_text(self, text: str, bold=False, italic=False, strikethrough=False, underline=False, code=False,
                       color="default"):
        data = {
            "type": "text",
            "href": None,
            "plain_text": text,
            "annotations": {
                "bold": bold,
                "italic": italic,
                "strikethrough": strikethrough,
                "underline": underline,
                "code": code,
                "color": color,
            },
            "text": {"content": text, "link": None},
        }
        self._res = [data]
        return self

    def add_plain_text(self, text: str, bold=False, italic=False, strikethrough=False, underline=False, code=False,
                       color="default"):
        data = {
            "type": "text",
            "href": None,
            "plain_text": text,
            "annotations": {
                "bold": bold,
                "italic": italic,
                "strikethrough": strikethrough,
                "underline": underline,
                "code": code,
                "color": color,
            },
            "text": {"content": text, "link": None},
        }
        self._res.append(data)
        return self

    def add_rich_text(self, rich_text):
        self._res.extend(rich_text._res)
        return self

    def __len__(self):
        return len(self._res)

    def __getitem__(self, item):
        return RichText([self._res[item]])

    def __repr__(self):
        return self.plain_text

    @property
    def res(self):
        return self._res
