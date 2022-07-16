import time
from pprint import pformat
from typing import Dict

import notion_client
from rich_text import RichText
from notion_property import *

_BLOCK_TYPES = {
    "paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "to_do", "toggle",
    "child_page", "child_database", "embed", "image", "video", "file", "pdf", "bookmark", "callout", "quote",
    "equation", "divider", "table_of_contents", "column", "column_list", "link_preview", "synced_block", "template",
    "link_to_page", "table", "table_row", "unsupported"
}


class Block(object):
    def __init__(self, client: notion_client.client.Client, block_id: str, block_res=None):
        self._block_res = block_res
        self._children = None
        self.client = client
        self.block_id = block_id

    def __repr__(self):
        return pformat(self.block_res)

    @property
    def type(self):
        return self.block_res["type"]

    @property
    def block_res(self):
        if getattr(self, "_block_res", None) is None:
            self._block_res = self.client.blocks.retrieve(self.block_id)
        return self._block_res

    @staticmethod
    def guess_block_type(block_res: Dict):
        _BLOCK_TYPES_ = {
            "paragraph": TextBlock,
            "heading_1": TextBlock,
            "heading_2": TextBlock,
            "heading_3": TextBlock,
            "file": FileBlock,
            "child_page": PageBlock,
            "child_database": DatabaseBlock,
        }
        block_type = block_res["type"]
        if block_type in _BLOCK_TYPES_:
            return _BLOCK_TYPES_[block_type]
        else:
            return Block

    def children(self):
        if getattr(self, "_children", None) is None:
            _children_res = self.client.blocks.children.list(self.block_id)
            self._children = []
            for children_block_res in _children_res["results"]:
                children_block_id = children_block_res["id"]
                type_block = self.guess_block_type(children_block_res)
                self._children.append(type_block(self.client, block_id=children_block_id, block_res=children_block_res))
        return self._children

    def append_children(self, type="paragraph", **kwargs):
        children_type = self.guess_block_type({"type": type})
        data = {"children": [children_type.template(**kwargs)]}
        _children_res = self.client.blocks.children.append(self.block_id, **data)
        self._children = []
        for children_block_res in _children_res["results"]:
            children_block_id = children_block_res["id"]
            type_block = self.guess_block_type(children_block_res)
            self._children.append(type_block(self.client, block_id=children_block_id, block_res=children_block_res))
        return self._children

    def archive(self):
        data = {
            "archived": True
        }
        res = self.client.blocks.update(block_id=self.block_id, **data)
        self._block_res = res
        return self

    @staticmethod
    def template(**kwargs):
        raise NotImplementedError


class PageBlock(Block):
    def __init__(self, client, block_id: str, block_res=None):
        super().__init__(client, block_id, block_res)

    @property
    def title(self):
        return self.block_res["child_page"]["title"]

    def as_page(self):
        return Page(self.client, self.block_id)

    def __repr__(self):
        return "PageBlock(" + pformat({"id": self.block_id, "title": self.title}) + ")"


class Page(PageBlock):
    def __init__(self, client, block_id: str, block_res=None, page_res=None):
        super().__init__(client, block_id, block_res)
        self._properties = None
        self.page_id = block_id
        self._page_res = page_res

    def as_block(self):
        return PageBlock(self.client, self.page_id)

    @property
    def page_res(self):
        if getattr(self, "_page_res", None) is None:
            self._page_res = self.client.pages.retrieve(self.page_id)
        return self._page_res

    @property
    def properties(self):
        if getattr(self, "_properties", None) is None:
            properties = self.page_res["properties"]
            name_list = list(properties.keys())
            id_list = [properties[name]["id"] for name in name_list]
            self._properties = dict(zip(name_list, id_list))
        return self._properties

    def retrieve_properties(self, name: str):
        assert name in self.properties.keys(), "Property {} not found, available names are {}".format(name,
                                                                                                      self.properties.keys())

        def retry():
            try:
                return self.client.pages.properties.retrieve(self.page_id, self.properties[name])
            except Exception as e:
                if str(e).startswith("429"):
                    print("Retrying query...")
                    time.sleep(1)
                    return retry()
                else:
                    raise e

        res = retry()
        property_type = guess_property_type(res)
        return property_type(res)

    def __repr__(self):
        return "Page(" + pformat({"id": self.page_id}) + ")"

    def archive(self):
        res = self.client.pages.update(page_id=self.page_id, archived=True)
        self._page_res = res

    def set_title(self, title: str, bold=False, italic=False, strikethrough=False, underline=False, code=False,
                  color="default"):
        data = {
            "properties": TitleProperty.template(text=title, bold=bold, italic=italic, strikethrough=strikethrough,
                                                 underline=underline, code=code, color=color)
        }
        res = self.client.pages.update(page_id=self.page_id, **data)
        self._page_res = res

    def set_property(self, name: str, property):
        data = {
            "properties": {
                name: property
            }
        }
        res = self.client.pages.update(page_id=self.page_id, **data)
        self._page_res = res


class TextBlock(Block):
    def __init__(self, client, block_id: str, block_res=None):
        super().__init__(client, block_id, block_res)
        self._rich_text = None
        self.POSSIBLE_TYPES = ["paragraph"]

    @property
    def plain_text(self):
        return self.rich_text.plain_text

    @property
    def rich_text(self):
        if getattr(self, "_rich_text", None) is None:
            self._rich_text = RichText(self.block_res[self.type]["rich_text"])
        return self._rich_text

    def __repr__(self):
        return "TextBlock(" + pformat({"type": self.type,
                                       "id": self.block_id,
                                       "plain_text": self.plain_text}) + ")"

    def set_plain_text(self, text: str, bold=False, italic=False, strikethrough=False, underline=False, code=False,
                       color="default"):
        data = {
            self.type: RichTextProperty.template(text=text, bold=bold, italic=italic, strikethrough=strikethrough,
                                                 underline=underline, code=code, color=color)
        }

        res = self.client.blocks.update(block_id=self.block_id, **data)
        self._rich_text = RichText(res[self.type]["rich_text"])
        self._block_res = res
        return self

    def set_rich_text(self, rich_text: RichText):
        data = {
            "paragraph": {
                "rich_text": rich_text.res}
        }
        res = self.client.blocks.update(block_id=self.block_id, **data)
        self._rich_text = RichText(res[self.type]["rich_text"])
        self._block_res = res
        return self

    def add_rich_text(self, rich_text: RichText):
        self.rich_text.add_rich_text(rich_text)
        data = {
            "paragraph": {
                "rich_text": self.rich_text.res}
        }
        res = self.client.blocks.update(block_id=self.block_id, **data)
        self._rich_text = RichText(res[self.type]["rich_text"])
        self._block_res = res

    @staticmethod
    def template(type="paragraph", text="", bold=False, italic=False, strikethrough=False, underline=False,
                 code=False, color="default", **kwargs):
        data = {
            "object": "block",
            "type": type,
            type: RichTextProperty.template(text=text, bold=bold, italic=italic, strikethrough=strikethrough,
                                            underline=underline, code=code, color=color)
        }
        return data


class FileBlock(Block):
    def __init__(self, client, block_id: str, block_res=None):
        super().__init__(client, block_id, block_res)

    @property
    def file_url(self):
        return self.block_res["file"]["external"]["url"]

    @staticmethod
    def template(extern_url, **kwargs):
        data = {
            "object": "block",
            "type": "file",
            "file": {
                "type": "external",
                "external": {
                    "url": extern_url
                }
            }
        }
        return data

    def __repr__(self):
        return "FileBlock(" + pformat({"id": self.block_id, "file_url": self.file_url}) + ")"


class DatabaseBlock(Block):
    def __init__(self, client, block_id: str, block_res=None):
        super().__init__(client, block_id, block_res)

    @property
    def title(self):
        return self.block_res["child_database"]["title"]

    def as_database(self):
        raise NotImplementedError

    def __repr__(self):
        return "DatabaseBlock(" + pformat({"id": self.block_id, "title": self.title}) + ")"
