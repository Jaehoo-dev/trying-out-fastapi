from enum import Enum
from typing import Dict, List, Optional, Union, Set

from fastapi import FastAPI, Path, Query, Body
from pydantic import BaseModel, Field, HttpUrl


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0,
                         description="The price must be greater than zero")
    tax: Optional[float] = None
    tags: Set[str] = set()
    images: Optional[List[Image]] = None


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


app = FastAPI()

fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: Optional[int] = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({'price_with_tax': price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Item,
    user: User,
    importance: int = Body(..., gt=0),
    q: Optional[str] = None
):
    # {
    #     "item": {
    #         "name": "Foo",
    #         "description": "The pretender",
    #         "price": 42.0,
    #         "tax": 3.2
    #     },
    #     "user": {
    #         "username": "dave",
    #         "full_name": "Dave Grohl"
    #     },
    #     "importance": 5
    # }
    results = {"item_id": item_id, "item": item,
               "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


@app.get("/items/")
async def read_items(q: Optional[str] = Query(
    None,
    alias="item-query",
    title="Query string",
    description="Query string for the items to search in the database \
        that have a good match",
    min_length=3,
    max_length=50,
    regex="^fixedquery$",
    deprecated=True,
)):
    results: Dict[str, Union[str, List[Dict[str, str]]]] = {
        "items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items/{item_id}")
async def read_items_by_query(
    *,
    item_id: int = Path(..., title="The ID of the item to get", gt=0, le=1000),
    q: str,
    size: float = Query(..., gt=0, lt=10.5)
):
    results: Dict[str, Union[int, str]] = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights
