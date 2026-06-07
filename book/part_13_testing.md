# Part 13: Testing

---

## Chapter 1: Unit & Integration Testing with Pytest

### 1. Introduction
Testing ensures code behaves as expected and prevents regressions during code updates. In modern FastAPI applications, writing asynchronous test suites using `pytest` and `httpx` is standard practice.

### 2. Concept Explanation
* **Why it exists**: Manually verification of routes is slow and error-prone. Automated testing validates routes, validation constraints, and database transactions instantly.
* **When to use it**: Every production-grade application.
* **When NOT to use it**: Throwaway scripts.
* **Advantages**: Prevents bugs, documents behavior, speeds up refactoring.
* **Disadvantages**: Writing and maintaining test suites requires initial time and effort.
* **Industry Use Cases**: CI/CD pipelines validating build stability before deployment.

### 3. Architecture Explanation
The test framework uses `pytest` and `httpx.AsyncClient` to simulate HTTP requests against the FastAPI app, overriding database dependencies to run tests in isolated environments.
```
pytest Run ---> AsyncClient (HTTP Mock) ---> FastAPI app (overridden dependencies) ---> SQLite/InMemory DB
```

### 4. Visual Workflow
```
[ Test Suite ] ---> GET /health ---> TestClient ---> App logic ---> Assert Status == 200
```

### 5. Real-World Scenario
An application needs to verify that the registration endpoint accepts valid payloads, rejects duplicate emails with a 400 Bad Request error, and does not write to the production database during testing.

### 6. Step-by-Step Implementation
1. Install testing packages: `pytest`, `pytest-asyncio`, `httpx`.
2. Configure a `conftest.py` file with database session and test client fixtures.
3. Write test functions with assertions.

### 7. Source Code Examples
#### Target Application (`main.py`)
```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Target App")

class Item(BaseModel):
    name: str

ITEMS_DB = {}

@app.post("/items", status_code=201)
async def create_item(item: Item):
    if item.name in ITEMS_DB:
        raise HTTPException(status_code=400, detail="Item already exists")
    ITEMS_DB[item.name] = item
    return {"name": item.name}
```

#### Test Suite (`test_main.py`)
```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app, ITEMS_DB

# Clear the database before each test
@pytest.fixture(autouse=True)
def clear_db():
    ITEMS_DB.clear()

@pytest.mark.asyncio
async def test_create_item_success():
    # Setup AsyncClient using ASGITransport for testing FastAPI app directly
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/items", json={"name": "Book"})
    
    assert response.status_code == 201
    assert response.json() == {"name": "Book"}

@pytest.mark.asyncio
async def test_create_item_duplicate():
    # Insert initial record
    ITEMS_DB["Book"] = {"name": "Book"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/items", json={"name": "Book"})
        
    assert response.status_code == 400
    assert response.json()["detail"] == "Item already exists"
```

### 8. API Testing Examples
Run the test suite using pytest:
```bash
pytest test_main.py -v
# Output:
# test_main.py::test_create_item_success PASSED   [ 50%]
# test_main.py::test_create_item_duplicate PASSED [100%]
```

### 9. Common Mistakes
Using a shared production database for testing, which leads to test data leakage and corrupted production records.

### 10. Best Practices
Override database dependencies in `conftest.py` using `app.dependency_overrides` to run tests against an isolated, clean test database (e.g., SQLite in-memory).

### 11. Interview Questions
* **Q: How do you mock database sessions when testing FastAPI routes?**
  * *A*: You can override database session dependencies in the test setup by updating `app.dependency_overrides[get_db] = get_test_db`, pointing it to a fixture that yields an isolated transaction.

### 12. Chapter Summary
Pytest and HTTPX support async API testing. Setting up database overrides and cleaning the database state between tests ensures reliable, isolated test execution.

### 13. Practice Exercises
Write a test verifying that the `/items` endpoint returns a 422 Unprocessable Entity error when the request body is empty.
