import pytest
import os
import motor.motor_asyncio
from gdmongolite_sample.schema import db

@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    test_db_name = "test_gdmongolite_fastapi"
    os.environ['MONGO_DB'] = test_db_name

    # Ensure the db object is using the correct database name
    db.database_name = test_db_name

    # Drop the database before tests run
    await db.client.drop_database(test_db_name)
    print(f"\nDropped database: {test_db_name} before tests")

    yield

    # Drop the database after all tests have completed
    await db.client.drop_database(test_db_name)
    print(f"\nDropped database: {test_db_name} after tests")
    if db.client:
        db.client.close()
