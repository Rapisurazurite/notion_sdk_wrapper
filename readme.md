**notion-sdk-wrapper is a wrapper for the Notion API, based on [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)**

This project is used for personal purposes, to make me easier to use the Notion API.
So I only wrote the code to satisfy my needs.

### Usage
This wrapper treats the blocks, pages, and properties as objects, and provides methods to access them.

Import and initialize a client using an integration token or an OAuth access token.
```python
import os
from notion_sdk_wrapper import NotionClient
notion_client = NotionClient(os.environ["NOTION_TOKEN"])
```

Retrieve a page by ID.
```python
page = notion_client.retrieve_page("https://www.notion.so/a-page-id")
print("title:", page.title)
print(page)
```
The result is a `Page` object.
```text
>>> title: A Page title
>>> Page({'id': 'xxxxxxxxxxxxxxxxxxxxxx'})
```

Retrieve a database by ID.
```python
database = notion_client.retrieve_database("https://www.notion.so/a-database-id")
print(database)
```
The result is a `Database` object.
```text
Database({'id': 'xxxxxxxxxxxxxxxxxxxxxx',
 'properties': {'Name': 'title',
                'Property': 'W%3An%5D',
                'Property 1': 'YEdI',
                'Property 2': 'Q%3BK%5C',
                'Property 3': 'qwwx',
                'Tags': 'UPcx'},
 'title': 'A Database title'})

```

Retrieve blocks in  page or database 
```python
print(page.children())
print(database.children())
```
It will return a list of object.

Update a block or a page
```python
from notion_sdk_wrapper import NumberProperty
page.set_properties("Property", property=NumberProperty.template(number=14114141))
page.set_title("test test test")

# I only wrote the code for text_block update.
text_block.set_plain_text("test test test")
```
Create a new page or block
```python
properties = {
    "Name": TitleProperty.template(text="test test"),
    "Property 3": RichTextProperty.template(text="test test"),
    "Property": NumberProperty.template(number=1211212),
    "Property 2": SelectProperty.template(name="ABCD"),
}

database.add_page(properties=properties)

page.append_block(type="paragraph", text="test test test")
```