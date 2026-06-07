# Part 15: Middleware

---

## Chapter 1: Custom Middleware, CORS, & Secure Headers

### 1. Introduction
Middleware functions run before and after every HTTP request, allowing you to intercept, modify, or audit request and response contexts globally.

### 2. Concept Explanation
* **Why it exists**: Many features (like adding security headers, verifying allowed domains, or tracking request durations) apply globally across all routes. Middleware centralizes this logic.
* **When to use it**: Cross-Origin Resource Sharing (CORS) configurations, adding secure headers, rate limiting, request tracing, global error handling.
* **When NOT to use it**: For route-specific business logic or authorization checks (where dependency injection is cleaner and more precise).
* **Advantages**: Centralized request auditing, automatic header updates, non-intrusive operations.
* **Disadvantages**: Heavy middleware processing increases API latency for all requests.
* **Industry Use Cases**: Injecting request IDs, blocking untrusted hosts, configuring CORS.

### 3. Architecture Explanation
Middleware sits between the ASGI server and the FastAPI router, processing requests before they hit endpoints and modifying responses before they return.
```
HTTP Request ---> [ CORS Middleware ] ---> [ Security Headers ] ---> [ Route Handler ]
                                                                             |
HTTP Response <--- [ CORS Middleware ] <--- [ Security Headers ] <-----------/
```

### 4. Visual Workflow
```
Client Call ---> [ Middleware: Process Request ] ---> [ Route Handler ] ---> [ Middleware: Process Response ] ---> Client
```

### 5. Real-World Scenario
An enterprise API needs to configure CORS to restrict requests to trusted domains, block requests from untrusted hosts, and add secure HTTP headers (like `X-Frame-Options` and `Content-Security-Policy`).

### 6. Step-by-Step Implementation
1. Import CORS, TrustedHost, and BaseHTTPMiddleware modules.
2. Configure CORS and TrustedHost middlewares.
3. Build a custom middleware class to append secure headers and track response latency.

### 7. Source Code Examples
```python
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="Middleware Enterprise Setup")

# 1. Enable Trusted Host Middleware (prevent HTTP Host Header attacks)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.corp.com"]
)

# 2. Enable CORS Middleware (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.corp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# 3. Custom Middleware for Security Headers and Performance Auditing
class SecurityHeadersAndTelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Process request and get response
        response = await call_next(request)
        
        # Calculate execution latency
        process_time = time.perf_counter() - start_time
        
        # Inject custom telemetry header
        response.headers["X-Process-Time"] = f"{process_time:.6f}s"
        
        # Inject security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

# Register custom middleware
app.add_middleware(SecurityHeadersAndTelemetryMiddleware)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### 8. API Testing Examples
Call the health check endpoint and inspect the response headers:
```bash
curl -I http://127.0.0.1:8000/health
# Output:
# HTTP/1.1 200 OK
# x-process-time: 0.001041s
# x-frame-options: DENY
# x-content-type-options: nosniff
# content-security-policy: default-src 'self'
# referrer-policy: strict-origin-when-cross-origin
```

### 9. Common Mistakes
Forgetting that middleware classes extending `BaseHTTPMiddleware` can conflict with routing contexts in streaming protocols (like WebSockets or Server-Sent Events).

### 10. Best Practices
For streaming or high-performance endpoints, implement ASGI-compatible middleware classes directly instead of inheriting from `BaseHTTPMiddleware`, to prevent memory buffering.

### 11. Interview Questions
* **Q: Why can `BaseHTTPMiddleware` cause issues when streaming responses?**
  * *A*: `BaseHTTPMiddleware` wraps response bodies in an iterator to allow editing headers after the route runs, which can buffer responses in memory and break streaming protocols like WebSockets or Server-Sent Events (SSE).

### 12. Chapter Summary
Middleware intercepts HTTP requests globally. Configuring CORS, TrustedHost, and custom security headers protects endpoints from common web vulnerabilities.

### 13. Practice Exercises
Write custom middleware that rejects requests containing a User-Agent header associated with known web scrapers or bots (e.g. `curl`).
