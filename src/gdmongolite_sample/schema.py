from gdmongolite import DB, Schema, Email, Positive
from pydantic import ConfigDict
db = DB()
class Product(Schema):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    price: Positive()
    email: Email
    tags: list[str] = []