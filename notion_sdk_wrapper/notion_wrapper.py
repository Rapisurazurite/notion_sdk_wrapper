from notion_blocks import Page, Block
from notion_client import Client
from notion_database import Database
from notion_property import *


class NotionClient:
    def __init__(self, NOTION_TOKEN: str):
        self.client = Client(auth=NOTION_TOKEN)

    def retrieve_page(self, page_id: str):
        page = Page(self.client, page_id)
        return page

    def retrieve_database(self, database_id: str):
        database = Database(self.client, database_id)
        return database

    def retrieve_block(self, block_id: str):
        res = self.client.blocks.retrieve(block_id)
        block_type = Block.guess_block_type(res)
        return block_type(self.client, block_id=block_id, block_res=res)


if __name__ == "__main__":
    import os

    notion_client = NotionClient(os.environ["NOTION_TOKEN"])
    draft_page = notion_client.retrieve_page("d0f6a4e6422d4dc89ff53de7de3e6c29")
    database = notion_client.retrieve_database("059a1599344841d09153c461ff8677fe")
    # database = notion_client.retrieve_database("fbd9f29624c142cf9f44bdc86da250a1")
    contents = database.children(filters={})
    #
    # properties = {
    #     "Name": TitleProperty.template(text="test test"),
    #     "Property 3": RichTextProperty.template(text="test test"),
    #     "Property": NumberProperty.template(number=1211212),
    #     "Property 2": SelectProperty.template(name="ABCD"),
    # }
    #
    # database.add_page(properties=properties)
    contents[0].set_property("Property", property=NumberProperty.template(number=14114141))
    contents[0].set_title("test test test")
    contents[0].set_property("Property 3", property=RichTextProperty.template(text="test test test"))
    print(database)