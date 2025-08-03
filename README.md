# gdmongolite Sample Trail
This sample project demonstrates how to use **gdmongolite**:
1. Configure the database connection in `.env`.  
2. Define your data model in `schema.py`.  
3. Run `python -m src.gdmongolite_sample.app` to insert and query data.  
## Expected Output
```
Products: [{'name':'Widget','price':9.99,'email':'support@example.com','tags':['test'], ...}]
```
## Testing
Use pytest to verify all functions:
```
pytest --maxfail=1 --disable-warnings -q
```
Include tests for insert, find, update, delete, pagination, and error handling.