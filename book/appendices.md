# Appendices

---

## Appendix A: Cheat Sheets

### 1. FastAPI Cheat Sheet
* **Instantiate App**: `app = FastAPI()`
* **Path Operations**:
  ```python
  @app.get("/items/{item_id}")
  async def read_item(item_id: int, q: str | None = None):
      return {"item_id": item_id, "q": q}
  ```
* **Inject Dependency**: `token: str = Depends(oauth2_scheme)`
* **Raise Exception**: `raise HTTPException(status_code=400, detail="Error message")`
* **Custom Response**: `return ORJSONResponse(content=data)`

### 2. Pydantic V2 Cheat Sheet
* **Model Definition**:
  ```python
  from pydantic import BaseModel, Field
  class User(BaseModel):
      id: int
      username: str = Field(..., min_length=3)
  ```
* **Serialization**: `data = user.model_dump()` (returns a dict) or `json_data = user.model_dump_json()` (returns a JSON string)
* **Validation**: `user = User.model_validate(raw_dict)`
* **Settings Management**:
  ```python
  from pydantic_settings import BaseSettings
  class Settings(BaseSettings):
      db_url: str
  ```

### 3. SQLAlchemy 2.0 Cheat Sheet
* **Async Engine**: `engine = create_async_engine("postgresql+asyncpg://...")`
* **Async Session**: `async_session = async_sessionmaker(engine, expire_on_commit=False)`
* **Model Class**:
  ```python
  class User(Base):
      __tablename__ = "users"
      id: Mapped[int] = mapped_column(primary_key=True)
      name: Mapped[str] = mapped_column(String(30))
  ```
* **Async Query**:
  ```python
  result = await session.execute(select(User).where(User.name == "Alice"))
  users = result.scalars().all()
  ```

### 4. Docker Cheat Sheet
* **Build Image**: `docker build -t app-name:latest .`
* **Run Container**: `docker run -d -p 8000:8000 --env-file .env app-name:latest`
* **Compose Up**: `docker compose up --build -d`
* **Prune Resources**: `docker system prune -a --volumes`

### 5. Kubernetes Cheat Sheet
* **Apply Config**: `kubectl apply -f deployment.yaml`
* **Get Pods**: `kubectl get pods -n production`
* **Log Streaming**: `kubectl logs -f pod-name`
* **Restart Deployment**: `kubectl rollout restart deployment/fastapi-deployment`

### 6. AWS Cheat Sheet
* **ECR Login**: `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin account_id.dkr.ecr.us-east-1.amazonaws.com`
* **ECS Update**: `aws ecs update-service --cluster app-cluster --service app-service --force-new-deployment`

---

## Appendix B: Production Deployment Checklist

* [ ] **Environment Security**: Secrets are loaded from AWS Secrets Manager or secure environment variables (no hardcoded passwords).
* [ ] **Non-Root User**: Dockerfile specifies `USER appuser` to run container processes securely.
* [ ] **Resource Limits**: Kubernetes deployment manifests define explicit CPU/Memory request and limit boundaries.
* [ ] **API Documentation**: Swagger and ReDoc pages are disabled (`docs_url=None`, `redoc_url=None`) in public production environments.
* [ ] **CORS Origins**: Trusted domains are configured in CORS middleware (no wildcard `*` allowed).
* [ ] **Logging & Monitoring**: JSON logs are piped to stdout, and `/metrics` and health routes (`/healthz`, `/readyz`) are exposed.
* [ ] **Database Connection Pool**: Database sessions are closed correctly, and `expire_on_commit` is set to `False`.
* [ ] **Gunicorn/Uvicorn**: Process managers are configured with Uvicorn worker classes to distribute loads across cores.

---

## Appendix C: Common Errors & Solutions

### 1. `RuntimeError: Expected ASGI message, but got...`
* **Cause**: Running an ASGI application (like FastAPI) using a WSGI server (like default Gunicorn) without specifying Uvicorn worker classes.
* **Solution**: Launch the server using the Uvicorn worker class:
  ```bash
  gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
  ```

### 2. `AttributeError: 'Coroutines' object has no attribute...`
* **Cause**: Forgetting to use the `await` keyword before calling an asynchronous database query or library function.
* **Solution**: Ensure all async calls are awaited:
  ```python
  # INCORRECT: result = session.execute(query)
  # CORRECT:
  result = await session.execute(query)
  ```

### 3. `MissingGreenlet: field access requires a greenlet...`
* **Cause**: Attempting to lazy-load related SQLAlchemy models synchronously inside an asynchronous session.
* **Solution**: Use `selectinload()` or `joinedload()` in your query to load the related tables eagerly:
  ```python
  # CORRECT:
  stmt = select(Employee).options(selectinload(Employee.department))
  ```
