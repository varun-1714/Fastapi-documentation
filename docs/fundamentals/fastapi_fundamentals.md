# Part 2: FastAPI Fundamentals

---

## Chapter 1: Introduction to FastAPI

### 1. Introduction
FastAPI is a modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints. Built on top of Starlette and Pydantic, it provides speed comparable to NodeJS and Go.

### 2. Concept Explanation
* **Why it exists**: Previous frameworks like Django and Flask did not natively support async programming, automatic request validation, or auto-generated docs, requiring multiple third-party libraries.
* **When to use it**: High-performance REST APIs, Microservices, ML/AI model serving, real-time WebSockets systems.
* **When NOT to use it**: Monolithic applications relying heavily on built-in server-side template rendering and built-in Admin panels (where Django shines).
* **Advantages**: High performance, developer speed, automatic API docs (Swagger/ReDoc), rapid data serialization and validation via Pydantic.
* **Disadvantages**: Relatively young ecosystem for complex components like built-in admin dashboards or full ORM integrations.
* **Industry Use Cases**: Netflix, Uber, and Microsoft utilize FastAPI for low-latency web services.

### 3. Architecture Explanation
FastAPI acts as an application layer utilizing Pydantic for schema verification, running on top of Starlette (a lightweight ASGI toolkit).
```
+----------------------------------------+
|               FastAPI                  |
+-------------------+--------------------+
|  Pydantic (Data)  |  Starlette (Web)   |
+-------------------+--------------------+
```

### 4. Visual Workflow
```
Client Request ---> ASGI Server (Uvicorn) ---> Starlette Router ---> Pydantic Validate ---> API Logic
```

### 5. Real-World Scenario
An API team wants to build a user microservice that processes 5,000 JSON payloads per second while generating automated documentation.

### 6. Step-by-Step Implementation
1. Install Python 3.13.
2. Initialize virtual environment.
3. Install FastAPI.

### 7. Source Code Examples
```python
from fastapi import FastAPI

app = FastAPI(title="FastAPI Fundamentals")

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI"}
```

### 8. API Testing Examples
Start application and run test:
```bash
curl -X GET http://127.0.0.1:8000/
# Response: {"message": "Welcome to FastAPI"}
```

### 9. Common Mistakes
Assuming FastAPI operates synchronously by default on all threads.

### 10. Best Practices
Declare routes `async def` when executing async IO, and regular `def` when running CPU-bound or blocking operations.

### 11. Interview Questions
* **Q: Why is FastAPI so fast?**
  * *A*: It is built on Starlette (an ASGI framework) and Pydantic (data parsing written in Rust), bypassing python-level validation loops.

### 12. Chapter Summary
FastAPI leverages type safety and high performance to simplify REST API development.

### 13. Practice Exercises
Create a status endpoint returning system uptime.

---

## Chapter 2: ASGI vs WSGI

### 1. Introduction
Web Server Gateway Interface (WSGI) is the synchronous interface standard for Python web apps, while Asynchronous Server Gateway Interface (ASGI) is the async successor.

### 2. Concept Explanation
* **Why it exists**: WSGI (PEP 3333) binds one thread per request, making it incapable of handling concurrent connections like WebSockets. ASGI (PEP 3156 successor) supports async IO.
* **When to use ASGI**: WebSockets, Server-Sent Events (SSE), concurrent requests.
* **When to use WSGI**: Legacy Django/Flask apps without async requirements.
* **Advantages of ASGI**: Asynchronous execution, WebSocket support, long-lived connections.
* **Disadvantages of ASGI**: Higher complexity when handling blocking dependencies.
* **Industry Use Cases**: Chat backends, high-concurrency microservices.

### 3. Architecture Explanation
WSGI calls a single callable for each request. ASGI handles a lifetime event cycle and communicates via receive/send channel loops.
```
WSGI:  Request ---> Thread ---> Process ---> Response (Blocks Thread)
ASGI:  Request ---> Event Loop ---> Yields Control ---> Coroutine resumes (Non-blocking)
```

### 4. Visual Workflow
```
+--------------------------------------------------------------+
| ASGI Server (Uvicorn)                                        |
|   Request 1 -> [Async Event Loop] -> pauses -> Resumes       |
|   Request 2 -> [Async Event Loop] -> processes immediately   |
+--------------------------------------------------------------+
```

### 5. Real-World Scenario
An application needs to support both standard CRUD REST routes and a live system log monitoring WebSocket.

### 6. Step-by-Step Implementation
Compare execution models using async and sync server setups.

### 7. Source Code Examples
```python
# ASGI Application Structure
async def app(scope, receive, send):
    assert scope['type'] == 'http'
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [[b'content-type', b'text/plain']],
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello, ASGI World!',
    })
```

### 8. API Testing Examples
Run this raw ASGI script with uvicorn:
```bash
uvicorn asgi_app:app --port 8000
curl http://127.0.0.1:8000/
# Output: Hello, ASGI World!
```

### 9. Common Mistakes
Deploying ASGI applications using legacy WSGI servers like Gunicorn with default sync workers (resulting in connection timeouts).

### 10. Best Practices
Deploy ASGI servers (Uvicorn, Hypercorn) using process managers like Gunicorn running Uvicorn workers.

### 11. Interview Questions
* **Q: Can ASGI run WSGI applications?**
  * *A*: Yes, using wrappers like `a2wsgi`, which translate WSGI callables to ASGI stateful machines.

### 12. Chapter Summary
ASGI is the modern standard allowing Python web apps to support asynchronous networks, streaming, and WebSockets.

### 13. Practice Exercises
Write an ASGI app that logs request scope contents.

---

## Chapter 3: FastAPI vs Django vs Flask vs Spring Boot

### 1. Introduction
Selecting the right backend architecture determines long-term scalability and project maintainability.

### 2. Concept Explanation
* **FastAPI**: Lightweight, asynchronous, high validation speed, autogenerated docs.
* **Flask**: Microframework, synchronous, highly customizable, manual setup.
* **Django**: Full-stack framework, built-in ORM, Admin Panel, template engine.
* **Spring Boot**: Java enterprise standard, robust, heavy dependency injection, slower initial boot.

| Feature | FastAPI | Flask | Django | Spring Boot |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python | Python | Python | Java |
| **Async** | Native | Added | Partial | Native (WebFlux)|
| **Validation** | Pydantic | Third-party | Django Forms | Hibernate |
| **Speed** | Excellent | Moderate | Moderate | Excellent |

### 3. Architecture Explanation
Comparing the structural weight of each framework:
```
FastAPI:   [Uvicorn] -> [FastAPI Router] -> [Pydantic Validation] (Thin layer)
Django:    [WSGI] -> [Middleware] -> [URL Routing] -> [Views] -> [ORM] -> [Template] (Heavy)
```

### 4. Visual Workflow
```
Client Request ---> [FastAPI: Validation + Serializer Built-in] ---> Response
Client Request ---> [Flask: Controller -> Schema Plugin -> Serializer Plugin] ---> Response
```

### 5. Real-World Scenario
Choosing a technology stack for an AI Startup requiring rapid API development, high data validation speed, and auto-generated API specifications.

### 6. Step-by-Step Implementation
Compare basic payload processing times and code sizes across configurations.

### 7. Source Code Examples
FastAPI payload parsing is declarative:
```python
from fastapi import FastAPI
from pydantic import BaseModel

class UserPayload(BaseModel):
    name: str
    email: str

app = FastAPI()

@app.post("/users")
def create_user(user: UserPayload):
    return {"message": f"Created user {user.name}"}
```

### 8. API Testing Examples
```bash
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d '{"name": "Alice", "email": "alice@corp.com"}'
# Response: {"message": "Created user Alice"}
```

### 9. Common Mistakes
Choosing Django for stateless high-speed APIs, creating unnecessary ORM and migration overhead.

### 10. Best Practices
Use Django for administrative dashboards and server-rendered sites. Use FastAPI for high-performance service networks.

### 11. Interview Questions
* **Q: Under what circumstances would you choose Flask over FastAPI?**
  * *A*: Only when dealing with legacy codebases or when requiring absolute minimalism without type safety constraints.

### 12. Chapter Summary
FastAPI bridges the gap between Flask's simplicity and Django's capabilities, while adding modern asynchronous performance.

### 13. Practice Exercises
Rewrite a simple Flask route handling variable paths in FastAPI.

---

## Chapter 4: Environment Setup & Project Structure

### 1. Introduction
A production-grade environment structure ensures consistent deployments and modular file layouts.

### 2. Concept Explanation
* **Why it exists**: An unstructured project code base leads to circular imports and unmaintainable modules.
* **When to use it**: Any enterprise-level FastAPI project.
* **When NOT to use it**: Quick single-file prototypes.
* **Advantages**: Modularity, testability, clean separation of concerns.
* **Disadvantages**: Initial boilerplate overhead.
* **Industry Use Cases**: Production web apps with distinct domain layers.

### 3. Architecture Explanation
We structure the app using a standard layered architecture:
```
src/
├── app/
│   ├── api/          # Route layers
│   ├── core/         # Config and security settings
│   ├── models/       # DB models (SQLAlchemy)
│   ├── schemas/      # Request/Response validation schemas (Pydantic)
│   └── services/     # Business logic
├── tests/            # Test suites
└── main.py           # Application entrypoint
```

### 4. Visual Workflow
```
[Main Entry] ---> [App Instance] ---> [Routers] ---> [Service Controllers] ---> [DB/Cache]
```

### 5. Real-World Scenario
Structuring an Enterprise CRM application with distinct routes for Customers, Invoices, and Analytics.

### 6. Step-by-Step Implementation
1. Create directories in python workspace.
2. Initialize `.env` and `config.py`.

### 7. Source Code Examples
`app/core/config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise API"
    DATABASE_URL: str
    REDIS_URL: str

    class Config:
        env_file = ".env"

settings = Settings(_env_file=".env")
```

### 8. API Testing Examples
Validate directory execution using python:
```bash
python -m unittest tests/test_main.py
```

### 9. Common Mistakes
Committing `.env` configuration files containing passwords or secret keys directly to GitHub.

### 10. Best Practices
Add `.env` to `.gitignore`. Load configs using Pydantic Settings management.

### 11. Interview Questions
* **Q: How do you prevent circular imports in FastAPI router layers?**
  * *A*: Separate business logic into services and use `APIRouter` in sub-modules, mounting them inside `main.py` using `app.include_router()`.

### 12. Chapter Summary
Clean structures avoid circular dependencies. Separating configuration, router patterns, and database operations forms the base of a clean API.

### 13. Practice Exercises
Set up a starter workspace using the directory structure outlined above.

---

## Chapter 5: First FastAPI App & Documentation (OpenAPI, Swagger, ReDoc)

### 1. Introduction
FastAPI leverages OpenAPI standards to generate interactive web documentation out of the box.

### 2. Concept Explanation
* **Why it exists**: Manually maintaining API documentation (e.g., Postman collections, Wiki pages) is time-consuming and often becomes outdated.
* **When to use it**: All REST APIs.
* **When NOT to use it**: Internal microservices where documentation is strictly disabled for security.
* **Advantages**: Automated generation, interactive client sandbox, up-to-date specs.
* **Disadvantages**: Schema documentation can leak internal APIs if public.
* **Industry Use Cases**: OpenAPI schemas integrated with developer portals.

### 3. Architecture Explanation
FastAPI generates a JSON file detailing routes, parameter configurations, and schema rules. This file is parsed by Swagger UI and ReDoc to render user interfaces.
```
FastAPI App ---> /openapi.json ---> Swagger UI (/docs)
                               ---> ReDoc (/redoc)
```

### 4. Visual Workflow
```
[Browser Client] ---> GET /docs ---> [Uvicorn Server] ---> OpenAPI JSON parser ---> Swagger UI Render
```

### 5. Real-World Scenario
An API engineer needs to expose interactive testing consoles for front-end developers working on mobile apps.

### 6. Step-by-Step Implementation
Create a FastAPI app with metadata parameters and launch it.

### 7. Source Code Examples
```python
from fastapi import FastAPI

app = FastAPI(
    title="Inventory API",
    description="Manage warehouse items securely",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/docs-alternative"
)

@app.get("/items", tags=["Inventory"])
def list_items():
    return [{"id": 1, "name": "Server Rack"}]
```

### 8. API Testing Examples
Run using Uvicorn:
```bash
uvicorn main:app --reload
# Access docs at http://127.0.0.1:8000/swagger
# Access alternative docs at http://127.0.0.1:8000/docs-alternative
```

### 9. Common Mistakes
Exposing API documentation URLs in production configurations.

### 10. Best Practices
Set `docs_url=None` and `redoc_url=None` in production environments:
```python
from os import getenv
app = FastAPI(docs_url=None if getenv("ENV") == "prod" else "/docs")
```

### 11. Interview Questions
* **Q: How can you customize Swagger UI layout configurations in FastAPI?**
  * *A*: You can modify `app.swagger_ui_parameters` or override HTML templates by custom routes serving custom static Swagger assets.

### 12. Chapter Summary
FastAPI generates robust API specifications automatically. Customizing route URLs and tag groupings makes it easier to navigate.

### 13. Practice Exercises
Add metadata tags, security protocols, and description fields to a new API endpoint and verify it on Swagger UI.
