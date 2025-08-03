from gdmongolite import DB, Schema, Email, Positive
from pydantic import ConfigDict
db = DB()
class Product(Schema):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    title: str
    description: str
    price: Positive()
    discountPercentage: float
    rating: float
    stock: int
    brand: str
    category: str
    thumbnail: str
    images: list[str] = []
    email: Email # Keeping this for now, though not in DummyJSON directly
    tags: list[str] = [] # Keeping this for now, though not in DummyJSON directly
