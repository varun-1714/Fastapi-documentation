# Part 10: Background Tasks

---

## Chapter 1: In-Process BackgroundTasks vs Distributed Celery Queues

### 1. Introduction
Modern web applications must respond to clients quickly. Long-running operations like sending emails, processing images, or running reports should be executed in the background to avoid blocking the HTTP response thread.

### 2. Concept Explanation
* **FastAPI BackgroundTasks**: An in-process task runner built into Starlette. It executes tasks on the same server process after returning the HTTP response.
* **Celery**: A distributed task queue that runs tasks asynchronously on separate worker processes, coordinating via a message broker (Redis or RabbitMQ).

| Feature | FastAPI BackgroundTasks | Celery Distributed Queue |
| :--- | :--- | :--- |
| **Execution** | Same process (shares CPU/RAM) | Separate worker processes |
| **Complexity** | Extremely simple (no extra services) | Higher (requires broker and workers) |
| **Reliability** | Tasks are lost if the server crashes | Tasks persist in the broker |
| **Use Case** | Lightweight tasks (e.g. logging) | Heavy tasks (e.g. PDF generation) |

### 3. Architecture Explanation
FastAPI `BackgroundTasks` execute inside the ASGI server event loop or thread pool. Celery offloads tasks to a broker, which queues them for pickup by dedicated worker processes.
```
FastAPI Router ---> (Local Task Queue) ---> Executes in-process
FastAPI Router ---> [ Redis Broker ] ---> [ Celery Worker Process ]
```

### 4. Visual Workflow
```
Client Call ---> HTTP Request ---> API returns 202 accepted ---> Task queued in Broker ---> Worker executes
```

### 5. Real-World Scenario
A newsletter portal needs to dispatch confirmation emails to new subscribers without delaying their registration flow.

### 6. Step-by-Step Implementation
1. Install Celery and Redis: `pip install celery redis`.
2. Configure both FastAPI native `BackgroundTasks` and a Celery app instance.
3. Build email dispatch handlers for both execution models.

### 7. Source Code Examples
```python
import time
from fastapi import FastAPI, BackgroundTasks
from celery import Celery

app = FastAPI(title="Email Notification Service")

# 1. Celery Configuration
# Redis is used as the message broker and backend database
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Celery Task Definition
@celery_app.task
def send_email_via_celery(recipient: str, message: str):
    print(f"[Celery Worker] Starting email task to {recipient}...")
    time.sleep(5)  # Simulate network latency sending email
    print(f"[Celery Worker] Email successfully sent to {recipient}!")
    return f"Sent to {recipient}"

# 2. FastAPI Native Background Task Function
def send_email_via_fastapi(recipient: str, message: str):
    print(f"[FastAPI Thread] Starting email task to {recipient}...")
    time.sleep(3)  # Simulate network latency
    print(f"[FastAPI Thread] Email successfully sent to {recipient}!")

# 3. Endpoints
@app.post("/subscribe/fastapi", status_code=202)
async def subscribe_native(email: str, background_tasks: BackgroundTasks):
    # Enqueue task in-process
    background_tasks.add_task(send_email_via_fastapi, email, "Welcome to our platform!")
    return {"status": "Accepted", "method": "FastAPI BackgroundTasks"}

@app.post("/subscribe/celery", status_code=202)
async def subscribe_celery(email: str):
    # Enqueue task out-of-process in Celery broker
    send_email_via_celery.delay(email, "Welcome to our enterprise platform!")
    return {"status": "Accepted", "method": "Celery Distributed Queue"}
```

### 8. API Testing Examples
Enqueuing task via Celery:
```bash
curl -X POST "http://127.0.0.1:8000/subscribe/celery?email=user%40corp.com"
# Response (returns immediately):
# {"status":"Accepted","method":"Celery Distributed Queue"}
```
In the terminal where Celery worker is running, you will see the task output:
```bash
celery -A main.celery_app worker --loglevel=info
# [info] Task tasks.send_email_via_celery[id-xxx] received
# [Celery Worker] Email successfully sent to user@corp.com!
```

### 9. Common Mistakes
Running CPU-heavy calculations inside FastAPI's native `BackgroundTasks`, which blocks the main event loop and slows down the web server.

### 10. Best Practices
Use native `BackgroundTasks` for light operations (like analytics events or logging). Use Celery (or Arq/Rq) with a dedicated worker cluster for resource-heavy operations (like PDF parsing or ML inference).

### 11. Interview Questions
* **Q: How does a Celery worker retrieve tasks from Redis?**
  * *A*: Celery uses a polling/blocking connection to Redis, retrieving tasks from a queue (implemented as a Redis list or sorted set) and executing them on a pool of worker threads or processes.

### 12. Chapter Summary
FastAPI's built-in `BackgroundTasks` are ideal for simple, low-overhead operations. Distributed queues like Celery scale to support complex, heavy, and reliable task processing across multiple servers.

### 13. Practice Exercises
Add an endpoint that checks the completion status of a Celery task using its task ID.
