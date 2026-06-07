# Part 8: MongoDB & Motor

---

## Chapter 1: Async MongoDB with Motor (Blog Backend)

### 1. Introduction
NoSQL document stores like MongoDB are well-suited for unstructured, dynamic data layouts. Motor is the recommended developer library for accessing MongoDB asynchronously in Python applications.

### 2. Concept Explanation
* **Why it exists**: Relational databases enforce strict schemas. Document databases store data as JSON-like documents, allowing flexible layouts. Motor provides non-blocking async drivers for MongoDB.
* **When to use it**: Content Management Systems (CMS), logging hubs, analytics datastores, catalogs with dynamic properties.
* **When NOT to use it**: Applications requiring complex ACID transactional joins across many collections (use relational DBs like PostgreSQL instead).
* **Advantages**: Flexible schemas, rapid read operations, horizontal scalability, native JSON compatibility.
* **Disadvantages**: Lack of strict schema enforcement by default, higher RAM consumption due to data duplication.
* **Industry Use Cases**: Blogs, catalogs, real-time analytics dashboards.

### 3. Architecture Explanation
Motor handles connection pools asynchronously. It integrates with FastAPI by using Pydantic models for validation and serialization before writing documents to MongoDB.
```
FastAPI Router ---> Motor AsyncClient ---> MongoDB Database (JSON Documents)
```

### 4. Visual Workflow
```
Incoming JSON -> Pydantic validator -> Cast to Dict -> Motor insert_one -> Document written
```

### 5. Real-World Scenario
A blogging platform needs an API to manage articles, allowing authors to attach variable tags, write comments, and retrieve articles by slug.

### 6. Step-by-Step Implementation
1. Install MongoDB and packages: `motor`, `pydantic`.
2. Define blog post validation schemas.
3. Configure the motor async client connection.
4. Implement CRUD endpoints and aggregation queries.

### 7. Source Code Examples
```python
from datetime import datetime, timezone
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, HTTPException, status, Body
from pydantic import BaseModel, Field

# MongoDB connection string
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.blog_database
posts_collection = db.get_collection("posts")

app = FastAPI(title="Blog Platform Backend")

# Pydantic Schemas
class Comment(BaseModel):
    author: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BlogPost(BaseModel):
    title: str = Field(..., min_length=5)
    slug: str
    content: str
    tags: List[str] = []
    comments: List[Comment] = []
    published: bool = True

class BlogPostResponse(BlogPost):
    id: str = Field(alias="_id")

# Helper to format MongoDB outputs
def format_post(post) -> dict:
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "slug": post["slug"],
        "content": post["content"],
        "tags": post.get("tags", []),
        "comments": post.get("comments", []),
        "published": post.get("published", True)
    }

# CRUD Endpoints
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: BlogPost = Body(...)):
    post_dict = post.model_dump()
    result = await posts_collection.insert_one(post_dict)
    new_post = await posts_collection.find_one({"_id": result.inserted_id})
    return format_post(new_post)

@app.get("/posts/{slug}")
async def get_post_by_slug(slug: str):
    post = await posts_collection.find_one({"slug": slug})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return format_post(post)

# MongoDB Aggregation: Count posts by tag
@app.get("/analytics/tags")
async def get_tag_analytics():
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    cursor = posts_collection.aggregate(pipeline)
    results = []
    async for doc in cursor:
        results.append({"tag": doc["_id"], "count": doc["count"]})
    return results
```

### 8. API Testing Examples
Create a blog post:
```bash
curl -X POST http://127.0.0.1:8000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "FastAPI with MongoDB Tutorial", "slug": "fastapi-mongodb", "content": "Learn how to use Motor...", "tags": ["python", "mongodb", "fastapi"]}'
# Response: {"id":"6660abcd...","title":"FastAPI with MongoDB Tutorial",...}
```
Query analytics of tags:
```bash
curl -X GET http://127.0.0.1:8000/analytics/tags
# Response: [{"tag":"python","count":1},{"tag":"fastapi","count":1}, ...]
```

### 9. Common Mistakes
Forgetting that MongoDB uses `_id` (an `ObjectId` instance) as its default primary key, which is not JSON-serializable by default in Python without conversion.

### 10. Best Practices
Write helper functions or custom Pydantic decorators to convert MongoDB `ObjectId` types to strings before serializing the response payload.

### 11. Interview Questions
* **Q: How does Motor handle thread execution under the hood?**
  * *A*: Motor wraps PyMongo (which is blocking) and delegates database operations to a thread pool, presenting a non-blocking coroutine-based API to the event loop.

### 12. Chapter Summary
Using Motor with MongoDB allows you to store dynamic JSON documents asynchronously. Pydantic schemas validate raw payloads, and MongoDB aggregation pipelines support fast analytics.

### 13. Practice Exercises
Add a route `/posts/{slug}/comments` that appends a comment document to the post's comments array.
