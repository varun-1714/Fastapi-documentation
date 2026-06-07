# Part 5: Dependency Injection

---

## Chapter 1: Dependency Injection Basics (`Depends()`)

### 1. Introduction
Dependency Injection (DI) is a software design pattern where objects or functions receive other objects or functions they depend on, rather than creating them internally. FastAPI features a powerful DI system driven by the `Depends()` function.

### 2. Concept Explanation
* **Why it exists**: Hard-coding resource instantiation (like database connections or config parameters) makes components difficult to test, mock, or share across routes.
* **When to use it**: Fetching database sessions, authenticating requests, validating API headers, retrieving shared system configurations.
* **When NOT to use it**: For simple internal helper operations that contain no state or external system dependencies.
* **Advantages**: Code reuse, modularity, easy testing (dependencies can be easily overridden).
* **Disadvantages**: Can trace call paths poorly if dependencies are deeply nested.
* **Industry Use Cases**: Injecting database connection pools, parsing user sessions from request headers.

### 3. Architecture Explanation
When a route is called, FastAPI inspects its parameters. If it detects `Depends(dependency_function)`, it executes the dependency first, passing its return value to the route handler.
```
HTTP Request ---> [ Executes Dependency: check_api_key ] ---> passes result ---> [ Route Handler ]
```

### 4. Visual Workflow
```
Client Request ---> [ Depends(verify_header) ] ---> Valid? Yes ---> [ Route Executes ]
                                                ---> Valid? No  ---> 401 Unauthorized
```

### 5. Real-World Scenario
An API requires an endpoint to authenticate incoming client requests by validating a custom API token header.

### 6. Step-by-Step Implementation
1. Define a validation dependency function.
2. Inject it into the target route using `Depends`.

### 7. Source Code Examples
```python
from fastapi import FastAPI, Depends, Header, HTTPException, status

app = FastAPI(title="Dependency Injection Basics")

async def verify_auth_token(x_auth_token: str = Header(..., description="API Auth Token")) -> str:
    if x_auth_token != "super-secret-key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Auth Token"
        )
    return x_auth_token

@app.get("/secure-data")
async def get_secure_data(token: str = Depends(verify_auth_token)):
    return {"message": "You accessed secure data!", "token_used": token}
```

### 8. API Testing Examples
Request with an invalid token:
```bash
curl -i -H "x-auth-token: wrong" http://127.0.0.1:8000/secure-data
# HTTP/1.1 401 Unauthorized
# {"detail":"Invalid or missing Auth Token"}
```
Request with a valid token:
```bash
curl -i -H "x-auth-token: super-secret-key" http://127.0.0.1:8000/secure-data
# HTTP/1.1 200 OK
# {"message":"You accessed secure data!","token_used":"super-secret-key"}
```

### 9. Common Mistakes
Forgetting that dependencies are executed on every request unless configured otherwise (FastAPI uses dependency caching within a single request cycle by default).

### 10. Best Practices
Use dependency caching (`use_cache=True`) when multiple endpoints share the same session context, to prevent creating duplicate connections.

### 11. Interview Questions
* **Q: How does FastAPI handle dependency caching?**
  * *A*: If a dependency is used multiple times in the same request path (e.g. nested sub-dependencies), FastAPI caches the result and returns it instead of re-running the dependency, unless `use_cache=False` is set.

### 12. Chapter Summary
`Depends()` makes routes clean and modular by separating resource acquisition and authorization checks from route logic.

### 13. Practice Exercises
Write a dependency that extracts user location from the `User-Agent` header and logs it.

---

## Chapter 2: Reusable & Nested Dependencies

### 1. Introduction
Dependencies can depend on other dependencies, allowing you to build modular dependency trees for complex applications.

### 2. Concept Explanation
* **Why it exists**: Instead of writing large, monolithic validation functions, dependencies can be broken down into small, single-purpose functions.
* **When to use it**: When validating user credentials requires verifying both the database connection and the authorization token.
* **When NOT to use it**: If nesting goes too deep, it can complicate debugging stack traces.
* **Advantages**: High modularity, testable components, clean architecture.
* **Disadvantages**: Can add minor request overhead if dependency caching is disabled.
* **Industry Use Cases**: Checking permissions against a database record.

### 3. Architecture Explanation
FastAPI resolves dependency graphs before calling the route handler.
```
         [ DB Connection ]
                 ^
                 | (nested)
[ verify_user ] ---> [ Route Handler ]
```

### 4. Visual Workflow
```
Client Call ---> [ get_db ] ---> [ verify_user (uses db) ] ---> [ Route Executed ]
```

### 5. Real-World Scenario
An API route requires verifying if a user is active and exists in the database.

### 6. Step-by-Step Implementation
1. Implement a mock DB connection dependency.
2. Implement a user retrieval dependency that depends on the DB connection.
3. Inject the user dependency into the route.

### 7. Source Code Examples
```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI(title="Nested Dependencies")

# Simulating a DB session dependency
def get_db_session():
    # In production, this would yield a SQLAlchemy AsyncSession
    db = {"users": {1: {"username": "admin", "role": "admin", "active": True}}}
    try:
        yield db
    finally:
        pass  # cleanup connection

# Nested dependency: Depends on get_db_session
def get_active_user(user_id: int, db: dict = Depends(get_db_session)):
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user["active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user

@app.get("/users/me")
async def read_user_me(current_user: dict = Depends(get_active_user)):
    return {"status": "authenticated", "user": current_user}
```

### 8. API Testing Examples
Request with user_id:
```bash
curl -X GET "http://127.0.0.1:8000/users/me?user_id=1"
# Response: {"status":"authenticated","user":{"username":"admin","role":"admin","active":true}}
```

### 9. Common Mistakes
Forgetting that generator-based dependencies (using `yield`) will pause after yielding, waiting to clean up until the request completes.

### 10. Best Practices
Keep generator setup and teardown logic minimal to prevent holding database connections open longer than necessary.

### 11. Interview Questions
* **Q: What happens if an exception is raised inside a route that uses a generator dependency (with `yield`)?**
  * *A*: The exception propagates to the generator. You can use a `try...finally` block inside the dependency to ensure cleanup code runs even if the route raises an error.

### 12. Chapter Summary
Nested dependencies allow you to build complex validation pipelines from simple, reusable components.

### 13. Practice Exercises
Add a third level to the dependency tree to verify the user has "admin" privileges.

---

## Chapter 3: Class-Based Dependencies

### 1. Introduction
Class-based dependencies allow you to group related dependency logic, configuration parameters, and stateful helpers within a single class structure.

### 2. Concept Explanation
* **Why it exists**: Functions cannot easily store configuration parameters or manage state across calls. Callable classes can accept settings in their constructor and execute logic in their `__call__` method.
* **When to use it**: Designing a reusable permission checker that accepts required roles, or a search filter with default limits.
* **When NOT to use it**: Simple dependencies that can be written in a few lines of code.
* **Advantages**: Clean encapsulation, parameterized initialization, supports inheritance.
* **Disadvantages**: Slightly more verbose than function-based dependencies.
* **Industry Use Cases**: Role-Based Access Control (RBAC) verification filters.

### 3. Architecture Explanation
FastAPI can use any callable object as a dependency. When a class instance is passed to `Depends()`, FastAPI executes its `__call__` method.
```
Route ---> Depends(RoleChecker(["admin", "editor"])) ---> __call__(request) ---> checks roles
```

### 4. Visual Workflow
```
Route: Requires ["admin"] ---> RoleChecker inspects request token ---> matches admin ---> allows access
```

### 5. Real-World Scenario
An enterprise API needs to restrict routes to users with specific roles, like "admin", "editor", or "viewer".

### 6. Step-by-Step Implementation
1. Define a class that accepts role requirements in its constructor.
2. Implement the `__call__` method to validate the request.

### 7. Source Code Examples
```python
from fastapi import FastAPI, Depends, Header, HTTPException, status

app = FastAPI(title="Class-Based Dependencies")

# Class-based role checker
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, x_user_role: str = Header(..., description="User role info")) -> str:
        if x_user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{x_user_role}' is not authorized. Allowed: {self.allowed_roles}"
            )
        return x_user_role

# Instantiate checkers
admin_only = RoleChecker(["admin"])
admin_or_editor = RoleChecker(["admin", "editor"])

@app.get("/admin/dashboard")
def get_dashboard(role: str = Depends(admin_only)):
    return {"message": "Welcome Admin!", "authorized_role": role}

@app.get("/content")
def get_content(role: str = Depends(admin_or_editor)):
    return {"message": "Welcome Editor or Admin!", "authorized_role": role}
```

### 8. API Testing Examples
Request dashboard with an unauthorized role:
```bash
curl -H "x-user-role: editor" http://127.0.0.1:8000/admin/dashboard
# Response: {"detail":"Role 'editor' is not authorized. Allowed: ['admin']"}
```
Request content with an authorized role:
```bash
curl -H "x-user-role: editor" http://127.0.0.1:8000/content
# Response: {"message":"Welcome Editor or Admin!","authorized_role":"editor"}
```

### 9. Common Mistakes
Instantiating the class checker inside the route declaration rather than reusing pre-configured class instances.
```python
# MISTAKE (creates a new instance every request):
# @app.get("/data")
# def get_data(role = Depends(RoleChecker(["admin"])))
```

### 10. Best Practices
Instantiate class-based dependencies globally (like `admin_only = RoleChecker(["admin"])`) and pass the instance to `Depends()`.

### 11. Interview Questions
* **Q: Can a class without a `__call__` method be used as a FastAPI dependency?**
  * *A*: Yes. If a class has an `__init__` constructor, you can pass the class itself (e.g. `Depends(MyClass)`). FastAPI will treat the constructor parameters as route inputs, instantiate the class, and pass the new instance to the route.

### 12. Chapter Summary
Class-based dependencies support parametrization, making it easy to create reusable authorization filters and database adapters.

### 13. Practice Exercises
Write a class-based dependency called `QueryFilter` that accepts default sorting and limits, and returns a dict of query params.
