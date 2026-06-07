# Part 14: Logging & Monitoring

---

## Chapter 1: Structured Logging with Loguru & Prometheus Metrics

### 1. Introduction
In production systems, traditional print statements are insufficient. Structured logging (writing logs in JSON format) and application metrics (like request counts and latency tracking) are critical for monitoring application health and debugging errors at scale.

### 2. Concept Explanation
* **Structured Logging**: Formatting log outputs as JSON. This allows logs to be easily parsed and searched by log aggregators (like Elasticsearch, AWS CloudWatch, or Datadog).
* **Metrics & Monitoring**: Tracking numeric values (e.g. latency, error rates, CPU usage) to build real-time dashboards and trigger alerts when anomalies occur.

| Component | Purpose | Tooling | Output Format |
| :--- | :--- | :--- | :--- |
| **Structured Logging** | Detailed event context for debugging | Loguru | JSON lines |
| **Metrics Tracking** | High-level performance statistics | Prometheus | Timeseries floats |

### 3. Architecture Explanation
The application logs structured JSON events using `loguru`. Prometheus instruments endpoints to track request rates and execution times, exposing a `/metrics` route for data collection.
```
Client Request ---> [ Prometheus Middleware ] ---> [ Route Handler ]
                          |                             |
                 Record latency metrics           Log event (Loguru JSON)
```

### 4. Visual Workflow
```
HTTP Request ---> [ Loguru Logger ] ---> JSON Formatter ---> stdout / CloudWatch log stream
```

### 5. Real-World Scenario
A production API needs to track request latency and error rates, outputting logs in JSON format for ingestion by an AWS CloudWatch agent.

### 6. Step-by-Step Implementation
1. Install logging and metrics packages: `loguru`, `prometheus-client`.
2. Configure Loguru to intercept standard logs and output JSON strings.
3. Add middleware to track request latency and update Prometheus metrics.
4. Expose the `/metrics` endpoint.

### 7. Source Code Examples
```python
import sys
import json
import time
from fastapi import FastAPI, Request, Response
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Structured Logging & Monitoring")

# 1. Configure Loguru for JSON Structured Logging
logger.remove()  # Remove default handler
def json_formatter(record):
    log_entry = {
        "timestamp": record["date"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "extra": record["extra"]
    }
    return json.dumps(log_entry) + "\n"

logger.add(sys.stdout, format=json_formatter, level="INFO")

# 2. Configure Prometheus Metrics
REQUEST_COUNT = Counter(
    "api_requests_total", "Total count of API requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds", "Histogram of request latency", ["endpoint"]
)

# 3. Latency Tracking Middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.perf_counter()
    endpoint = request.url.path
    method = request.method
    
    # Process request
    response: Response = await call_next(request)
    
    # Record metrics
    duration = time.perf_counter() - start_time
    status_code = str(response.status_code)
    
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    
    # Log request details in JSON format
    logger.bind(latency=duration, status=status_code, client_ip=request.client.host).info(
        f"Request processed: {method} {endpoint}"
    )
    
    return response

# 4. Endpoints
@app.get("/items")
def list_items():
    return [{"id": 1, "name": "Standard Server"}]

@app.get("/metrics")
def get_metrics():
    # Expose metrics to Prometheus scraper
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### 8. API Testing Examples
Request items endpoint to generate metrics and logs:
```bash
curl http://127.0.0.1:8000/items
```
Review the structured log output in the terminal:
```json
{"timestamp": "2026-06-07T12:35:10.123", "level": "INFO", "message": "Request processed: GET /items", "module": "main", "function": "monitor_requests", "line": 45, "extra": {"latency": 0.0054, "status": "200", "client_ip": "127.0.0.1"}}
```
Query the `/metrics` endpoint to verify Prometheus tracks the request:
```bash
curl http://127.0.0.1:8000/metrics
# Output:
# api_requests_total{endpoint="/items",method="GET",http_status="200"} 1.0
```

### 9. Common Mistakes
Writing logs in unstructured text format in production, making it difficult to search and filter logs across thousands of records.

### 10. Best Practices
Set unique request IDs (Correlation IDs) for every request and include them in both logs and response headers to trace calls across microservices.

### 11. Interview Questions
* **Q: Why should you use structured JSON logging instead of plain text logs in production?**
  * *A*: Structured JSON logs allow log aggregation tools (like Elasticsearch, AWS CloudWatch, or Datadog) to parse and index fields (such as latency, status codes, or user IDs) automatically, making it easy to search, filter, and alert on specific event conditions.

### 12. Chapter Summary
Structured logging formats logs as JSON for easy parsing. Prometheus metrics track performance in real time, exposing data to monitoring dashboards.

### 13. Practice Exercises
Add a Correlation ID middleware that generates a unique UUID for each request, includes it in the response headers, and appends it to all Loguru logs.
