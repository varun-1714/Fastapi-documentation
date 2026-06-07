# Part 24: Interview Preparation

This section provides senior-level interview questions and answers across core backend architectural categories.

---

## Chapter 1: Core FastAPI Interview Questions

### Q1: Explain how FastAPI handles asynchronous and synchronous route handlers differently.
**Answer:**
FastAPI is built on Starlette, which runs an ASGI event loop. 
- When a route is declared using `async def`, FastAPI runs it directly on the main event loop thread. The code must not block the thread; any IO-bound operation must be awaited.
- When a route is declared using regular `def`, FastAPI runs it in an external thread pool (using `anyio.to_thread.run_sync`). This prevents blocking operations (like standard file IO or database calls) from freezing the main event loop.

### Q2: What is ASGI and how does it differ from WSGI?
**Answer:**
- **WSGI (Web Server Gateway Interface)**: A synchronous standard where each request is mapped to a single execution thread. It cannot handle long-lived concurrent connections like WebSockets or Server-Sent Events (SSE).
- **ASGI (Asynchronous Server Gateway Interface)**: An asynchronous successor to WSGI. It supports non-blocking requests and bi-directional communication, allowing a single thread to handle thousands of concurrent connections.

### Q3: What is dependency caching in FastAPI?
**Answer:**
If a dependency is used multiple times in the same request path (e.g. by a route and a sub-dependency), FastAPI caches the return value by default. It reuses the cached value instead of running the dependency again. You can disable this behavior by setting `use_cache=False` (e.g., `Depends(get_db, use_cache=False)`).

### Q4: How do you handle file uploads in a memory-efficient way?
**Answer:**
Use `UploadFile` instead of `bytes`. `bytes` forces the entire file to be loaded into memory. `UploadFile` utilizes a temporary spool file, storing files in memory only up to a limit before writing them to disk. It also provides helper methods like `read()` and `seek()` to stream file data.

### Q5: How do you configure CORS in a FastAPI application?
**Answer:**
CORS is configured by registering `CORSMiddleware` in the application middleware stack:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Chapter 2: Pydantic V2 Interview Questions

### Q6: What are the main improvements of Pydantic V2 over Pydantic V1?
**Answer:**
Pydantic V2 is rewritten in Rust, which makes serialization and validation up to 50x faster. It also introduces strict/lax validation modes, renames validation methods (e.g., `dict()` to `model_dump()`), separates settings management into `pydantic-settings`, and features a cleaner custom validator API using `@field_validator` and `@model_validator`.

### Q7: Explain the difference between `@field_validator` and `@model_validator`.
**Answer:**
- `@field_validator` validates a single field (or list of fields) individually. It is a class method that runs during the field validation phase.
- `@model_validator` validates the entire model. It runs after individual fields are validated and is used to validate rules that span multiple fields (like comparing passwords).

### Q8: What is strict validation mode in Pydantic V2?
**Answer:**
In default (lax) mode, Pydantic coerces types where possible (e.g. converting the string `"123"` into the integer `123`). In strict mode, Pydantic raises a validation error if the input type does not match the model annotation exactly.

---

## Chapter 3: SQLAlchemy 2.0 Interview Questions

### Q9: Why is `expire_on_commit=False` recommended in async database setups?
**Answer:**
By default, SQLAlchemy expires object attributes when a transaction commits, forcing it to reload data from the database on subsequent access. In async applications, accessing these expired attributes will trigger blocking synchronous database queries, raising an error or freezing the event loop.

### Q10: How do you prevent the N+1 query problem when fetching relationships?
**Answer:**
Use eager loading options in your queries:
- `selectinload()`: Runs a second SELECT query to load related child objects, which is recommended for one-to-many relationships.
- `joinedload()`: Uses a SQL JOIN to load related child objects in a single query, which is recommended for many-to-one relationships.

---

## Chapter 4: JWT & Security Interview Questions

### Q11: Where should you store access tokens and refresh tokens in browser clients?
**Answer:**
- **Access Tokens**: Store in application memory (variables). Avoid storing them in `localStorage` or `sessionStorage` because they are vulnerable to Cross-Site Scripting (XSS) attacks.
- **Refresh Tokens**: Store in secure, `HttpOnly`, `Secure`, and `SameSite=Strict` cookies. This protects them from XSS and limits exposure to Cross-Site Request Forgery (CSRF).

### Q12: How do you implement Role-Based Access Control (RBAC) in FastAPI?
**Answer:**
Implement a class-based dependency that accepts authorized roles, retrieves the current user's role, and raises an HTTP 403 Forbidden error if the user is not authorized:
```python
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
```

---

## Chapter 5: Docker & Kubernetes Interview Questions

### Q13: Why should you run containers as a non-root user?
**Answer:**
By default, Docker containers run as the root user. If an attacker compromises the container (e.g. through a code vulnerability), they gain root privileges inside the container, which can allow them to escape the container and compromise the host system.

### Q14: Explain the difference between liveness and readiness probes.
**Answer:**
- **Liveness Probe**: Determines if the container is running. If the liveness check fails, Kubernetes restarts the container.
- **Readiness Probe**: Determines if the container is ready to accept network traffic. If the readiness check fails, Kubernetes removes the pod from the service load balancer, stopping traffic without restarting the container.

---

## Chapter 6: AWS & Cloud Architecture Interview Questions

### Q15: How do you secure database credentials in an AWS container deployment?
**Answer:**
Store credentials in AWS Secrets Manager or Systems Manager Parameter Store. Reference the secret in the ECS Task Definition, injecting it into the container as an environment variable at runtime. Do not commit credentials to source control or hard-code them in Docker images.

---

## Chapter 7: System Design Interview Questions

### Q16: How do you design a system that handles heavy file processing requests without blocking the web server?
**Answer:**
Use an asynchronous task queue architecture:
1. The client uploads the file to an object store (e.g., AWS S3) and calls the API.
2. The API saves a record in the database, pushes a task containing the file URL to a message broker (e.g., Redis or RabbitMQ), and returns an HTTP 202 Accepted response to the client.
3. Dedicated worker processes (e.g., Celery workers) pull tasks from the broker, process the files, and update the database status.
4. The client polls the API or receives a WebSocket notification when processing completes.
```
Client ---> API Gateway ---> [ API Web Node ] ---> Returns 202
                                   |
                             Enqueues Task
                                   v
                             [ Redis Queue ] <--- [ Worker Nodes ] ---> Updates DB
```
