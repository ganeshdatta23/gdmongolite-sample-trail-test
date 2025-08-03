import pytest
import asyncio
from gdmongolite_sample.schema import db, Product
@pytest.mark.asyncio
async def test_insert_and_find(tmp_path, monkeypatch):
    # Use a test database
    monkeypatch.setenv('MONGO_DB', 'testdb')
    # Insert and retrieve
    await db.Product.insert({"name":"Gizmo","price":19.99,"email":"test@example.com"})
    found = await db.Product.find(name__regex='Gizmo').to_list()
    assert any(p['name']=='Gizmo' for p in found)