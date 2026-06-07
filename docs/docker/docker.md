# Part 17: Docker Containerization

---

## Chapter 1: Multi-Stage Dockerfiles & Docker Compose Orchestration

### 1. Introduction
Containerization package applications and their dependencies into a single deployable image, ensuring consistency across development, testing, and production environments. Docker is the industry standard for containerization.

### 2. Concept Explanation
* **Why it exists**: Deploying applications directly to servers often leads to "it works on my machine" bugs due to mismatched library versions or missing configuration dependencies. Docker isolates applications from the host environment.
* **When to use it**: Every production deployment, cloud environment, or microservices network.
* **When NOT to use it**: Extremely small, simple scripts that execute locally without external dependencies.
* **Advantages**: Consistent deployments, isolated dependencies, fast scaling, multi-stage builds to optimize image size.
* **Disadvantages**: Minor performance overhead compared to running natively on the host OS.
* **Industry Use Cases**: Packaging microservices, running test pipelines, deploying to Kubernetes clusters.

### 3. Architecture Explanation
A multi-stage Docker build uses separate phases (stages) in the same `Dockerfile`. The build stage installs build tools and compiles dependencies. The run stage copies only the final compiled code into a minimal base image, reducing the size of the production image.
```
Build Stage (Python-Dev) ---> Compiles pip packages ---> Copies to run stage
Run Stage (Python-Slim)  ---> Copies compiled packages ---> Runs as non-root user
```

### 4. Visual Workflow
```
[ Codebase ] ---> Docker Build ---> Docker Image (Run Stage Only) ---> Container Launch
```

### 5. Real-World Scenario
A development team needs to deploy a FastAPI application that connects to PostgreSQL and Redis. The production image must be optimized for size, run securely as a non-root user, and launch alongside its database and cache dependencies using Docker Compose.

### 6. Step-by-Step Implementation
1. Write an optimized, multi-stage `Dockerfile`.
2. Configure a `docker-compose.yml` file linking the web app, PostgreSQL, and Redis services.
3. Configure environment variables for container coordination.

### 7. Source Code Examples
#### Production-Ready `Dockerfile`
```dockerfile
# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final minimal execution image
FROM python:3.13-slim AS runner

WORKDIR /app

# Copy built packages from builder stage
COPY --from=builder /root/.local /root/.local
COPY . /app

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Run as non-root user for security
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Multi-Service Orchestration `docker-compose.yml`
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://admin:password@db:5432/app_db
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d app_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 8. Running and Testing Examples
Build and launch the entire stack:
```bash
docker compose up --build -d
```
Check running container status:
```bash
docker compose ps
# Output:
# Name                  Command               State           Ports
# fastapi_cache_1    docker-entrypoint.sh    Up      0.0.0.0:6379->6379/tcp
# fastapi_db_1       docker-entrypoint.sh    Up      0.0.0.0:5432->5432/tcp
# fastapi_web_1      uvicorn main:app...     Up      0.0.0.0:8000->8000/tcp
```

### 9. Common Mistakes
Running Docker containers as the root user, which gives attackers root access to the host server if the application is compromised.

### 10. Best Practices
Always use multi-stage builds to keep production images small. Run containers as a non-root user (`USER appuser`), and use Docker Compose health checks (`pg_isready`) to ensure database dependencies are ready before launching the web service.

### 11. Interview Questions
* **Q: Why should you use multi-stage builds in production Dockerfiles?**
  * *A*: Multi-stage builds separate the build environment (which requires compilers, build tools, and headers) from the runtime environment. This ensures the final production image contains only the compiled dependencies, reducing the image size and minimizing the attack surface.

### 12. Chapter Summary
Docker containerizes applications for consistent environments. Multi-stage builds keep images small, and Docker Compose coordinates multi-container stacks.

### 13. Practice Exercises
Add a health check block to the `web` service in `docker-compose.yml` that queries `/healthz` every 10 seconds.
