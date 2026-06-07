# Part 22: Microservices Architecture

---

## Chapter 1: E-Commerce Microservices Platform (API Gateway & Event Dispatcher)

### 1. Introduction
A microservices architecture splits monolithic applications into small, independent services that communicate over networks. Designing microservices requires setting up API Gateways to route external traffic and Event Brokers to coordinate services asynchronously.

### 2. Concept Explanation
* **Why it exists**: Monolithic codebases can become large, difficult to scale, and hard to update across different teams. Microservices allow services to be deployed, scaled, and updated independently.
* **When to use it**: Large-scale applications with multiple development teams, differing scaling needs per feature (e.g. scaling checkout more than reviews).
* **When NOT to use it**: Early-stage startups or small projects where network complexity outweighs organizational scale.
* **Advantages**: Independent deployments, technology flexibility, faults isolation, localized scaling.
* **Disadvantages**: Data consistency is harder to maintain (requires distributed transactions), networking overhead, complex debugging.
* **Industry Use Cases**: E-commerce checkouts, payment processing systems, inventory management.

### 3. Architecture Explanation
The architecture uses an API Gateway as the single entrypoint for external clients, routing requests to internal microservices. The services communicate asynchronously using an Event Broker (Redis Streams or RabbitMQ) to handle events like orders placed or inventory updated.
```
Public Client ---> [ API Gateway Router ] ---> routes to HTTP services
                                                     |
                     [ Service 1 (Order) ] ---> Publishes "OrderPlaced"
                                                     |
                                            [ Redis Event Broker ]
                                                     |
                                                     v
                     [ Service 2 (Inventory) ] <--- Subscribes & updates
```

### 4. Visual Workflow
```
Place Order ---> Gateway ---> Order Service (Saves Order) ---> Publishes Event ---> Inventory Service updates stock
```

### 5. Real-World Scenario
An E-Commerce company wants to separate its checkout flow from its inventory system. When a customer places an order, the Order service saves the order details and publishes an event. The Inventory service listens for the event and adjusts stock levels asynchronously.

### 6. Step-by-Step Implementation
1. Configure an API Gateway routing requests to service endpoints.
2. Build the Order microservice to handle checkout.
3. Build an event dispatcher that publishes messages to Redis Streams.
4. Implement the Inventory service to consume events.

### 7. Source Code Examples
#### 1. API Gateway Router (`gateway.py`)
```python
from fastapi import FastAPI, Request, HTTPException, status
import httpx

app = FastAPI(title="API Gateway")

SERVICES_ROUTING = {
    "orders": "http://localhost:8001",
    "inventory": "http://localhost:8002"
}

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_gateway(service_name: str, path: str, request: Request):
    service_base_url = SERVICES_ROUTING.get(service_name)
    if not service_base_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Service '{service_name}' not registered."
        )

    # Reconstruct route url
    target_url = f"{service_base_url}/{path}"
    
    # Forward headers and request body
    body = await request.body()
    headers = dict(request.headers)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=dict(request.query_params),
                content=body,
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, 
                detail=f"Failed to connect to internal service: {e}"
            )
```

#### 2. Order Service with Redis Event Publisher (`order_service.py`)
```python
import json
import redis.asyncio as aioredis
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="Order Service")
redis_client = aioredis.from_url("redis://localhost:6379/0")

class Order(BaseModel):
    product_id: int
    quantity: int

@app.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout(order: Order):
    order_data = order.model_dump()
    order_data["status"] = "created"
    
    # Publish "OrderPlaced" event to Redis Stream
    event_payload = {
        "event_type": "OrderPlaced",
        "data": json.dumps(order_data)
    }
    await redis_client.xadd("ecommerce_events", event_payload)
    
    return {"message": "Order placed successfully", "order": order_data}
```

### 8. API Testing Examples
1. Launch the services on separate ports:
```bash
# Gateway
uvicorn gateway:app --port 8000
# Order Service
uvicorn order_service:app --port 8001
```
2. Call the order checkout endpoint through the API Gateway:
```bash
curl -X POST http://127.0.0.1:8000/orders/checkout \
  -H "Content-Type: application/json" \
  -d '{"product_id": 901, "quantity": 2}'
# Response routed through Gateway:
# {"message":"Order placed successfully","order":{"product_id":901,"quantity":2,"status":"created"}}
```

### 9. Common Mistakes
Using synchronous HTTP calls for all inter-service communication, which couples microservices and leads to cascading failures if one service goes down.

### 10. Best Practices
Use asynchronous message queues (such as RabbitMQ, Kafka, or Redis Streams) for state-changing events. Implement circuit breakers and retries for HTTP calls to handle temporary network errors.

### 11. Interview Questions
* **Q: What is the purpose of the API Gateway pattern in microservices?**
  * *A*: An API Gateway acts as the single entrypoint for all clients, abstracting the internal microservices structure. It handles routing, authentication, rate-limiting, and telemetry logging, reducing client-side complexity.

### 12. Chapter Summary
Microservices improve scalability but add network complexity. API gateways handle client-facing routing, and asynchronous brokers coordinate services without coupling them.

### 13. Practice Exercises
Add a retry decorator with exponential backoff to the gateway's HTTP request handler to handle temporary network timeouts.
