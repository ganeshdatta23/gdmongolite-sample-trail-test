import pytest
from fastapi.testclient import TestClient
from gdmongolite_sample.api import app
from gdmongolite_sample.schema import db, Product
from bson import ObjectId

@pytest.mark.asyncio
async def test_create_product():
    client = TestClient(app)
    response = client.post(
        "/products/",
        json={
            "title": "Test Product",
            "description": "A product for testing",
            "price": 10.0,
            "discountPercentage": 5.0,
            "rating": 4.5,
            "stock": 100,
            "brand": "TestBrand",
            "category": "TestCategory",
            "thumbnail": "test.jpg",
            "images": ["test1.jpg", "test2.jpg"],
            "email": "test@example.com",
            "tags": ["test", "sample"]
        },
    )
    assert response.status_code == 200
    product = response.json()
    assert product["title"] == "Test Product"
    assert "id" in product
    # Verify insertion in DB
    db_product = await db.Product.find_one({"_id": ObjectId(product["id"])})
    assert db_product is not None
    assert db_product["title"] == "Test Product"

@pytest.mark.asyncio
async def test_read_products():
    await db.Product.insert({"title": "Product1", "description": "", "price": 10.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandX", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []})
    await db.Product.insert({"title": "Product2", "description": "", "price": 20.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 20, "brand": "BrandY", "category": "cat2", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []})

    client = TestClient(app)
    response = client.get("/products/")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 2
    assert any(p["title"] == "Product1" for p in products)

@pytest.mark.asyncio
async def test_read_single_product():
    inserted_product = await db.Product.insert({"title": "Single Product", "description": "", "price": 10.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandX", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []})
    product_id = str(inserted_product.data["inserted_id"])

    client = TestClient(app)
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    product = response.json()
    assert product["title"] == "Single Product"
    assert product["id"] == product_id

@pytest.mark.asyncio
async def test_update_product():
    inserted_product = await db.Product.insert({"title": "Product to Update", "description": "", "price": 10.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandX", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []})
    product_id = str(inserted_product.data["inserted_id"])

    client = TestClient(app)
    response = client.put(
        f"/products/{product_id}",
        json={
            "title": "Updated Product",
            "price": 15.0
        },
    )
    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["title"] == "Updated Product"
    assert updated_product["price"] == 15.0

    db_product = await db.Product.find_one({"_id": ObjectId(product_id)})
    assert db_product["title"] == "Updated Product"
    assert db_product["price"] == 15.0

@pytest.mark.asyncio
async def test_delete_product():
    inserted_product = await db.Product.insert({"title": "Product to Delete", "description": "", "price": 10.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandX", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []})
    product_id = str(inserted_product.data["inserted_id"])

    client = TestClient(app)
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Product deleted successfully"}

    db_product = await db.Product.find_one({"_id": ObjectId(product_id)})
    assert db_product is None

@pytest.mark.asyncio
async def test_aggregate_category_price():
    await db.Product.insert_many([
        {"title": "A", "description": "", "price": 10.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandX", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []},
        {"title": "B", "description": "", "price": 20.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandY", "category": "cat1", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []},
        {"title": "C", "description": "", "price": 30.0, "discountPercentage": 0.0, "rating": 4.0, "stock": 10, "brand": "BrandX", "category": "cat2", "thumbnail": "", "images": [], "email": "test@example.com", "tags": []}
    ])

    client = TestClient(app)
    response = client.get("/products/aggregation/category_price")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 2
    assert {"_id": "cat1", "averagePrice": 15.0} in result
    assert {"_id": "cat2", "averagePrice": 30.0} in result
