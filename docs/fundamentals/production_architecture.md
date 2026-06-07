# Part 16: Production Architecture

---

## Chapter 1: Exception Handling, Versioning, Health Checks & ORJSON

### 1. Introduction
Deploying web APIs to production requires standardizing error responses, managing API versions cleanly as codebases evolve, implementing container health probes, and optimizing serialization speed.

### 2. Concept Explanation
* **Global Exception Handling**: Intercepts unhandled errors globally, preventing server crashes and returning standardized, secure error messages to clients.
* **API Versioning**: Ensures changes to API endpoints do not break integrations for existing clients (usually handled via URL path prefixes like `/api/v1`).
* **Health Checks**: Standardized routes (e.g. `/healthz`) that container orchestrators (like Kubernetes) query to determine if a container is running and ready to accept traffic.
* **ORJSONResponse**: An optimized FastAPI response class that uses `orjson` (a fast Python JSON library written in Rust) to serialize output payloads, replacing the default JSON serializer.

### 3. Architecture Explanation
The application structures routes under versioned API routers, maps exceptions to custom handler functions, and uses `ORJSONResponse` for fast serialization.
```
Client Request ---> [ Versioned Router: /v1 ] ---> [ ORJSONResponse ] ---> Client
                           |
                     Raises Exception ---> [ Global Exception Handler ] ---> JSON Error
```

### 4. Visual Workflow
```
Kubernetes Probes ---> GET /healthz ---> Checks DB/Redis connection ---> HTTP 200 (OK)
                                                                    ---> HTTP 503 (Failed)
```

### 5. Real-World Scenario
An API team needs to transition their services to production. The setup must return standardized error payloads, expose a health probe that checks database status, support versioned URL paths, and optimize serialization for large JSON payloads.

### 6. Step-by-Step Implementation
1. Install `orjson`.
2. Define custom exceptions and error handlers.
3. Configure versioned APIRouters.
4. Expose liveness and readiness health checks.

### 7. Source Code Examples
```python
from fastapi import FastAPI, APIRouter, Request, status, HTTPException
from fastapi.responses import ORJSONResponse

# 1. Custom Exceptions
class EnterpriseDatabaseException(Exception):
    def __init__(self, detail: str):
        self.detail = detail

# 2. Main App Configuration with ORJSON as the default serializer
app = FastAPI(
    title="Production Ready Enterprise API",
    default_response_class=ORJSONResponse
)

# 3. Global Exception Handlers
@app.exception_handler(EnterpriseDatabaseException)
async def db_exception_handler(request: Request, exc: EnterpriseDatabaseException):
    return ORJSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": "DatabaseOperationFailed", "message": exc.detail}
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"error": "ClientRequestError", "message": exc.detail}
    )

# 4. Versioned API Routers
v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

@v1_router.get("/users")
def get_users_v1():
    # Return large mock payload (orjson serializes this faster than default JSON)
    return {"version": "v1", "users": [{"id": i, "name": f"User {i}"} for i in range(1000)]}

@v2_router.get("/users")
def get_users_v2():
    return {"version": "v2", "data": {"active_users": []}}

app.include_router(v1_router)
app.include_router(v2_router)

# 5. Production Health Checks
@app.get("/healthz", status_code=status.HTTP_200_OK)
async def liveness_probe():
    # Simple check to confirm the container is running
    return {"status": "alive"}

@app.get("/readyz", status_code=status.HTTP_200_OK)
async def readiness_probe():
    # Check external connections (simulated database check)
    db_ok = True  # In production, run select 1 query
    if not db_ok:
        raise EnterpriseDatabaseException("Database connection timed out.")
    return {"status": "ready", "database": "connected"}
```

### 8. API Testing Examples
Call V1 endpoint to check versioning and response speed:
```bash
curl http://127.0.0.1:8000/v1/users
```
Trigger the database exception to test the global exception handler:
```bash
# Simulating a database failure on readiness probe
curl -i http://127.0.0.1:8000/readyz
# Response:
# HTTP/1.1 200 OK
# {"status":"ready","database":"connected"}
```

### 9. Common Mistakes
Forgetting that `orjson` serializes dataclasses, UUIDs, and datetimes natively, but custom user objects still require custom encoder functions.

### 10. Best Practices
Set up distinct liveness (`/healthz`) and readiness (`/readyz`) probes. The liveness probe should check if the server is running. The readiness probe should verify connections to external resources (like databases and Redis) before the load balancer sends traffic to the container.

### 11. Interview Questions
* **Q: Why should you separate liveness and readiness health checks?**
  * *A*: Liveness probes determine if the container needs to be restarted. Readiness probes determine if the container is ready to accept traffic. If a database goes down temporarily, you want to stop sending traffic to the container (readiness fails) without restarting the web server (liveness passes).

### 12. Chapter Summary
Global error handlers protect internal stack traces. Versioned routers ensure API backwards compatibility. Using ORJSON increases serialization speed, and health probes allow orchestrators to monitor container health.

### 13. Practice Exercises
Add a v1 endpoint `/error` that raises an unhandled `EnterpriseDatabaseException`, and verify the custom JSON payload returned to the client.
