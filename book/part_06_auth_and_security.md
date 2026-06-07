# Part 6: Authentication & Security

---

## Chapter 1: Hashing, JWTs & Enterprise Auth System

### 1. Introduction
Securing web APIs requires robust authentication (verifying identity) and authorization (verifying permissions). In modern web design, JSON Web Tokens (JWT) are the standard for stateless authorization.

### 2. Concept Explanation
* **Why it exists**: Session-state authentication requires storing session data on the server, which does not scale horizontally. JWTs encode user identity in a signed token, allowing stateless authorization.
* **When to use it**: Single Page Applications (SPAs), Mobile client integrations, Microservice communication.
* **When NOT to use it**: If tokens must be immediately revocable at any time (unless a token blacklist is managed in a high-speed database like Redis).
* **Advantages**: Stateless validation, scalability, self-contained payload data.
* **Disadvantages**: Hard to invalidate before expiration, vulnerable if the signing key is compromised.
* **Industry Use Cases**: OAuth2 login systems, Single Sign-On (SSO) gateways.

### 3. Architecture Explanation
A standard JWT auth flow features two tokens: short-lived Access Tokens (e.g. 15 mins) and long-lived Refresh Tokens (e.g. 7 days) stored in secure HTTP-only cookies to request new access tokens.
```
Client ---> POST /login ---> Returns Access Token & Sets Refresh Token Cookie
Client ---> GET /data (Bearer Header) ---> Auth Middleware Validates Signature ---> Success
```

### 4. Visual Workflow
```
+--------+             +--------------+             +--------------+
| Client | --(Login)-->|  Auth Route  | --(Verify)-->| Hashed DB pwd|
|        | <--Token--- |              | --(Sign JWT) |              |
+--------+             +--------------+             +--------------+
```

### 5. Real-World Scenario
An enterprise API needs a secure registration and login system with Role-Based Access Control (RBAC), using cryptographically signed tokens to protect endpoints.

### 6. Step-by-Step Implementation
1. Install security libraries: `passlib[bcrypt]`, `pyjwt`, `python-multipart`.
2. Construct a JWT helper module for token generation and validation.
3. Build user registration, login, and authorization routes.

### 7. Source Code Examples
```python
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# Config Constants
SECRET_KEY = "super-secret-jwt-signing-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Crypto Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Enterprise Auth System")

# Pydantic Schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"  # default role

class UserResponse(BaseModel):
    username: str
    email: EmailStr
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Mock Database
USERS_DB = {}

# Security Utilities
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        user = USERS_DB.get(username)
        if user is None:
            raise credentials_exception
        return user
    except jwt.InvalidTokenError:
        raise credentials_exception

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role"
            )
        return current_user

# Endpoints
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    if user.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    user_entry = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "role": user.role
    }
    USERS_DB[user.username] = user_entry
    return user_entry

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin-only", response_model=UserResponse)
def get_admin_data(current_user: Annotated[dict, Depends(RoleChecker(["admin"]))]):
    return current_user
```

### 8. API Testing Examples
1. Register user:
```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "superadmin", "email": "admin@corp.com", "password": "securepassword", "role": "admin"}'
```
2. Login to get JWT access token:
```bash
curl -X POST http://127.0.0.1:8000/token \
  -F "username=superadmin" \
  -F "password=securepassword"
# Response: {"access_token":"eyJhbGci...","token_type":"bearer"}
```
3. Call admin endpoint:
```bash
curl -X GET http://127.0.0.1:8000/admin-only \
  -H "Authorization: Bearer <access_token>"
```

### 9. Common Mistakes
Storing the signing key (`SECRET_KEY`) directly in source code or using a weak, easily guessable key.

### 10. Best Practices
Store secret keys in environment variables (`.env`) loaded via settings, and use a strong key generated using cryptographically secure methods:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 11. Interview Questions
* **Q: Why should refresh tokens be stored differently than access tokens?**
  * *A*: Access tokens are sent frequently in API headers and are vulnerable to interception. Refresh tokens are used rarely and should be stored in secure, `HttpOnly` and `SameSite=Strict` cookies to protect them from Cross-Site Scripting (XSS) attacks.

### 12. Chapter Summary
A secure authentication pipeline hashes passwords using `bcrypt` and handles stateless authorization using signed JWTs. Role-based middleware enforces access control at the route level.

### 13. Practice Exercises
Extend the API to support token invalidation by maintaining a Redis-backed token blacklist.

---

## Chapter 2: OWASP API Security & Vulnerability Mitigation

### 1. Introduction
Web APIs are target to security vulnerabilities like SQL Injection (SQLi), Cross-Site Scripting (XSS), and Cross-Site Request Forgery (CSRF). Mitigating these risks is a core requirement of secure API development.

### 2. Concept Explanation
* **SQL Injection (SQLi)**: Occurs when untrusted user input is concatenated directly into SQL query strings, allowing attackers to execute arbitrary database commands.
* **Cross-Site Scripting (XSS)**: Occurs when an application renders untrusted input without sanitization, allowing attackers to execute malicious scripts in the user's browser.
* **Cross-Site Request Forgery (CSRF)**: Occurs when a malicious site tricks a user's browser into executing an unauthorized action on a site where they are logged in.

### 3. Mitigation Strategies

| Vulnerability | Mechanism | Mitigation in FastAPI |
| :--- | :--- | :--- |
| **SQL Injection** | Dynamic query manipulation | Use SQLAlchemy parameterization or ORM functions. |
| **XSS** | Script injection in HTML pages | Sanitize HTML inputs using `bleach`. Render text safely. |
| **CSRF** | Hijacked authentication cookies | Use CORS origin controls and CSRF double-submit cookies. |

### 4. Visual Workflow
```
SQL Injection Attack:
Input: ' OR '1'='1 ---> ORM Parameterized Query ---> Escapes inputs safely ---> Safe DB execution
```

### 5. Real-World Scenario
An API endpoint accepts search input. If the developer constructs the query using string interpolation (e.g. `f"SELECT * FROM products WHERE name = '{query}'"`), an attacker can extract the entire database schema.

### 6. Step-by-Step Implementation
1. Configure SQLAlchemy to enforce parameterized queries.
2. Install CORS middleware to control allowed origins.

### 7. Source Code Examples
```python
# Prevention of SQL Injection using SQLAlchemy ORM (Parameterized Queries)
from sqlalchemy.orm import Session
from sqlalchemy import text

# SAFE: SQLAlchemy automatically parameterizes inputs
def get_user_by_name_safe(db: Session, username: str):
    # Parameterized query under the hood
    return db.execute(
        text("SELECT * FROM users WHERE name = :username"), 
        {"username": username}
    ).fetchall()

# UNSAFE: Concatenating strings is vulnerable to injection!
def get_user_by_name_unsafe(db: Session, username: str):
    return db.execute(
        text(f"SELECT * FROM users WHERE name = '{username}'")
    ).fetchall()
```

### 8. API Testing Examples
Attempting SQL Injection on a parameterized route will treat the payload as a literal string, returning no results instead of executing the injected SQL.
```bash
# Attempted SQL Injection input: "admin' OR '1'='1"
curl "http://127.0.0.1:8000/users/search?name=admin%27%20OR%20%271%27%3D%271"
# Returns 404/Empty safely because no user is literally named "admin' OR '1'='1"
```

### 9. Common Mistakes
Using raw string concatenation inside SQL execution calls under the assumption that the input has already been sanitized.

### 10. Best Practices
Always query databases using modern ORMs (SQLAlchemy, SQLModel) or parameterized query bindings.

### 11. Interview Questions
* **Q: How does using an ORM prevent SQL Injection vulnerabilities?**
  * *A*: ORMs separate the query structure from the input parameters. Input parameters are sent separately to the database engine as placeholders, ensuring they are treated as literal values rather than executable code.

### 12. Chapter Summary
Securing APIs requires validating all inputs, using parameterized queries, sanitizing HTML outputs, and configuring CORS origins.

### 13. Practice Exercises
Write a middleware wrapper that adds secure HTTP headers (e.g. `X-Frame-Options: DENY`, `Content-Security-Policy`) to all API responses.
