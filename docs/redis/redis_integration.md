# Part 9: Redis Integration

---

## Chapter 1: Redis Caching, OTP & Rate Limiting

### 1. Introduction
Redis is an open-source, in-memory key-value data structure store used as a database, cache, and message broker. Because it operates in-memory, it provides sub-millisecond read/write speeds, making it ideal for caching, rate-limiting, and storing temporary sessions.

### 2. Concept Explanation
* **Why it exists**: Primary databases are too slow for high-frequency operations like tracking login attempts or serving static dashboard numbers. Redis provides high-speed key-value access.
* **When to use it**: Rate-limiting APIs, caching query results, managing login sessions, storing temporary verification tokens.
* **When NOT to use it**: Storing large, complex relational datasets that require ACID guarantees.
* **Advantages**: Fast operations, support for TTL (Time-to-Live) key expiration, pub-sub messaging, built-in data types (hashes, sets, lists).
* **Disadvantages**: Data is held in memory, which is expensive; data loss can occur if persistence options (RDB/AOF) are misconfigured.
* **Industry Use Cases**: Session stores, API rate limiters, database query caching layers.

### 3. Architecture Explanation
The application uses Redis as an in-memory storage layer alongside its primary database. FastAPI endpoints write and read keys from Redis asynchronously.
```
FastAPI Router ---> Async Redis Client ---> Redis In-Memory Storage
```

### 4. Visual Workflow
```
Client Call ---> [ Rate Limiter Check ] ---> Exceeded? Yes ---> 429 Too Many Requests
                                       ---> Exceeded? No  ---> [ Process Request ]
```

### 5. Real-World Scenario
An authentication service needs to send a One-Time Password (OTP) to a user's phone, expire the token after 5 minutes, and limit users to 3 login attempts per minute.

### 6. Step-by-Step Implementation
1. Install Redis and packages: `redis`, `fastapi`.
2. Configure the async Redis client connection.
3. Build utility classes for rate limiting and OTP storage.
4. Implement endpoints for OTP generation and verification.

### 7. Source Code Examples
```python
import random
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, status, Depends

# Redis Connection URI
REDIS_URL = "redis://localhost:6379/0"
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(title="OTP Authentication & Rate Limiting System")

# Helper: Rate Limiting Dependency
class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds

    async def __call__(self, client_ip: str):
        key = f"rate_limit:{client_ip}"
        current_requests = await redis_client.get(key)

        if current_requests and int(current_requests) >= self.requests_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later."
            )
        
        # Increment request count
        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            if not current_requests:
                await pipe.expire(key, self.window_seconds)
            await pipe.execute()

# Define specific limiters
ip_rate_limiter = RateLimiter(requests_limit=5, window_seconds=60)

# OTP Endpoints
@app.post("/otp/generate")
async def generate_otp(phone: str, _=Depends(ip_rate_limiter)):
    otp = str(random.randint(100000, 999999))
    otp_key = f"otp:{phone}"
    
    # Store OTP with a 5-minute (300-second) TTL
    await redis_client.set(otp_key, otp, ex=300)
    
    # In production, dispatch this via an SMS gateway
    return {"message": "OTP generated successfully", "otp_sent": otp}

@app.post("/otp/verify")
async def verify_otp(phone: str, otp: str):
    otp_key = f"otp:{phone}"
    stored_otp = await redis_client.get(otp_key)
    
    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired or not requested"
        )
    
    if stored_otp != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Delete token after successful validation
    await redis_client.delete(otp_key)
    return {"message": "OTP verification successful"}
```

### 8. API Testing Examples
1. Generate an OTP:
```bash
curl -X POST "http://127.0.0.1:8000/otp/generate?phone=%2B123456789"
# Response: {"message":"OTP generated successfully","otp_sent":"489102"}
```
2. Verify with the generated OTP code:
```bash
curl -X POST "http://127.0.0.1:8000/otp/verify?phone=%2B123456789&otp=489102"
# Response: {"message":"OTP verification successful"}
```
3. Exceed the rate limit by calling the generate endpoint 6 times in a row:
```bash
# 6th request will output:
# {"detail":"Rate limit exceeded. Try again later."}
```

### 9. Common Mistakes
Forgetting to set a Time-To-Live (TTL) on temporary keys, causing Redis memory usage to grow indefinitely.

### 10. Best Practices
Always set an explicit expiry (`ex`) when saving tokens in Redis. Use transactional pipelines (`multi/exec`) to group related commands and save network roundtrips.

### 11. Interview Questions
* **Q: How does Redis handle key eviction when memory is full?**
  * *A*: Redis uses an eviction policy configured in `redis.conf` (e.g. `allkeys-lru`, `volatile-lru`, `noeviction`). When memory limits are reached, Redis evicts keys according to the selected policy.

### 12. Chapter Summary
Redis provides sub-millisecond in-memory caching and session validation. Using Redis pipelines and key expiration allows you to build reliable, high-speed rate limiters and OTP verification flows.

### 13. Practice Exercises
Implement a cached endpoint `/products/{id}` that checks Redis first, and only falls back to a mock database query if the key is not cached.
