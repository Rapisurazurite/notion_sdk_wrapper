import time

from notion_client import Client
from notion_blocks import *
from rich_text import RichText


class Database(Block):
    def __init__(self, client: Client, block_id: str, block_res=None):
        super(Database, self).__init__(client, block_id, block_res)
        self.database_id = block_id
        self._database_res = None
        self._properties = None

    @property
    def database_res(self):
        if getattr(self, "_database_res", None) is None:
            self._database_res = self.client.databases.retrieve(self.database_id)
        return self._database_res

    @property
    def title(self):
        return RichText(self.database_res["title"]).plain_text

    @property
    def properties(self):
        if getattr(self, "_properties", None) is None:
            properties = self.database_res["properties"]
            name_list = list(properties.keys())
            id_list = [properties[name]["id"] for name in name_list]
            self._properties = dict(zip(name_list, id_list))
        return self._properties

    def __repr__(self):
        return "Database(" + pformat({
            "id": self.database_id,
            "title": self.title,
            "properties": self.properties
        }) + ")"

    # Note: query method has a limit of frequency of calls to Notion API
    # So, we will retry it if we get a 429 error
    def query(self, filters: Dict = None, start_cursor: str = None):
        data = {
            "filters": filters,
            "start_cursor": start_cursor,
            "page_size": 100
        }

        def retry():
            try:
                return self.client.databases.query(self.database_id, **data)
            except Exception as e:
                if str(e).startswith("429"):
                    print("Retrying query...")
                    time.sleep(1)
                    return retry()
                else:
                    raise e

        res = retry()

        results = res["results"]
        has_more = res["has_more"]
        next_cursor = res["next_cursor"]

        return results, has_more, next_cursor

    def query_all(self, filters=None):
        if filters is None:
            filters = {}

        results = []
        has_more = True
        start_cursor = None
        while has_more:
            cur_res, has_more, start_cursor = self.query(filters, start_cursor)
            results.extend(cur_res)
            print("Got {} results".format(len(results)))
        return results

    def children(self, filters=None):
        if getattr(self, "_children", None) is None:
            _children_res = self.query_all(filters)
            self._children = []
            for children_page_res in _children_res:
                children_page_id = children_page_res["id"]
                self._children.append(Page(self.client, block_id=children_page_id, page_res=children_page_res))
        return self._children

    def add_page(self, properties: Dict):
        data = {
            "parent": {
                "database_id": self.database_id
            },
            "properties": properties
        }
        res = self.client.pages.create(**data)
        return Page(self.client, block_id=res["id"], page_res=res)
