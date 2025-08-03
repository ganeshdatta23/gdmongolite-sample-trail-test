import pytest
import asyncio
import httpx
import os
from gdmongolite_sample.schema import db, Product

@pytest.fixture(autouse=True)
async def setup_and_teardown(monkeypatch):
    monkeypatch.setenv('MONGO_DB', 'testdb')
    # Ensure the db object is using the correct database name
    db.database_name = 'testdb'
    # Clear all collections in the test database before each test
    for collection_name in await db.client[db.database_name].list_collection_names():
        await db.client[db.database_name][collection_name].delete_many({})
    yield
    # Clear all collections in the test database after each test
    for collection_name in await db.client[db.database_name].list_collection_names():
        await db.client[db.database_name][collection_name].delete_many({})

@pytest.mark.asyncio
async def test_insert_many_and_find():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://dummyjson.com/products")
        data = response.json()
        products_data = data["products"]

    products_to_insert = []
    for product_data in products_data:
        product_to_insert = {
            "title": product_data.get("title", "No Title"),
            "description": product_data.get("description", "No Description"),
            "price": product_data.get("price", 0.0),
            "discountPercentage": product_data.get("discountPercentage", 0.0),
            "rating": product_data.get("rating", 0.0),
            "stock": product_data.get("stock", 0),
            "brand": product_data.get("brand", "No Brand"),
            "category": product_data.get("category", "No Category"),
            "thumbnail": product_data.get("thumbnail", ""),
            "images": product_data.get("images", []),
            "email": "dummy@example.com",
            "tags": ["dummy", "json"]
        }
        products_to_insert.append(product_to_insert)

    await db.Product._collection.insert_many(products_to_insert)
    all_products = await db.Product.find().to_list()
    assert len(all_products) == len(products_to_insert)
    assert any(p['title'] == 'iPhone 9' for p in all_products)

@pytest.mark.asyncio
async def test_update_one():
    await db.Product.insert({"title": "Laptop X", "description": "", "price": 1000.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 50, "brand": "BrandA", "category": "electronics", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []})
    product = await db.Product.find_one({"title": "Laptop X"})
    assert product is not None
    old_price = product["price"]
    await db.Product.update_one({"_id": product["_id"]}, {"$set": {"price": old_price + 100}})
    updated_product = await db.Product.find_one({"_id": product["_id"]})
    assert updated_product["price"] == old_price + 100

@pytest.mark.asyncio
async def test_delete_many():
    await db.Product._collection.insert_many([
        {"title": "Product1", "description": "", "price": 10.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 5, "brand": "BrandA", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []},
        {"title": "Product2", "description": "", "price": 20.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 15, "brand": "BrandB", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []},
        {"title": "Product3", "description": "", "price": 30.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 8, "brand": "BrandA", "category": "cat2", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []}
    ])
    deleted_count = await db.Product.delete_many({"stock": {"$lt": 10}})
    assert deleted_count.deleted_count == 2
    remaining_products = await db.Product.find().to_list()
    assert len(remaining_products) == 1
    assert remaining_products[0]["title"] == "Product2"

@pytest.mark.asyncio
async def test_aggregation():
    await db.Product._collection.insert_many([
        {"title": "A", "description": "", "price": 10.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandX", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []},
        {"title": "B", "description": "", "price": 20.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandY", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []},
        {"title": "C", "description": "", "price": 30.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandX", "category": "cat2", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []}
    ])
    result = await db.Product.aggregate([
        {"$group": {"_id": "$category", "totalPrice": {"$sum": "$price"}}},
        {"$sort": {"_id": 1}}
    ]).to_list()
    assert len(result) == 2
    assert result[0]["_id"] == "cat1"
    assert result[0]["totalPrice"] == 30.0
    assert result[1]["_id"] == "cat2"
    assert result[1]["totalPrice"] == 30.0
