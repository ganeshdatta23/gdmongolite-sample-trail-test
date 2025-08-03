import asyncio
from gdmongolite_sample.schema import db, Product
async def main():
    # Insert a sample product
    await db.Product.insert({"name":"Widget","price":9.99,"email":"support@example.com","tags":["test"]})
    # Query all products
    products = await db.Product.find().to_list()
    print("Products:", products)
if __name__ == '__main__':
    asyncio.run(main())