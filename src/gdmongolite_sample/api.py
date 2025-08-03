from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from gdmongolite_sample.schema import db, Product
from bson import ObjectId

app = FastAPI()

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: dict):
        field_schema.update(type="string")

class ProductIn(BaseModel):
    title: str
    description: str
    price: float
    discountPercentage: float
    rating: float
    stock: int
    brand: str
    category: str
    thumbnail: str
    images: List[str] = []
    email: EmailStr
    tags: List[str] = []

class ProductOut(ProductIn):
    id: PyObjectId = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

@app.on_event("startup")
async def startup_db_client():
    # Ensure the DB client is initialized
    _ = db.client

@app.on_event("shutdown")
async def shutdown_db_client():
    if db.client:
        db.client.close()

@app.post("/products/", response_model=ProductOut)
async def create_product(product: ProductIn):
    new_product_result = await db.Product.insert(product.dict(by_alias=True))
    if not new_product_result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to insert product")
    created_product = await db.Product.find_one({"_id": new_product_result.inserted_id})
    if not created_product:
        raise HTTPException(status_code=500, detail="Failed to retrieve inserted product")
    return created_product

@app.get("/products/", response_model=List[ProductOut])
async def read_products():
    products = await db.Product.find().to_list()
    return products

@app.get("/products/{product_id}", response_model=ProductOut)
async def read_product(product_id: str):
    product = await db.Product.find_one({"_id": ObjectId(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: str, product: ProductIn):
    update_result = await db.Product.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": product.dict(by_alias=True, exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found or no changes made")
    updated_product = await db.Product.find_one({"_id": ObjectId(product_id)})
    if not updated_product:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated product")
    return updated_product

@app.delete("/products/{product_id}", response_model=dict)
async def delete_product(product_id: str):
    delete_result = await db.Product.delete_one({"_id": ObjectId(product_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@app.get("/products/aggregation/category_price", response_model=List[dict])
async def aggregate_category_price():
    result = await db.Product.aggregate([
        {"$group": {"_id": "$category", "averagePrice": {"$avg": "$price"}}},
        {"$sort": {"averagePrice": -1}}
    ]).to_list()
    return result
