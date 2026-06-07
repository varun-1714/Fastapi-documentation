# Part 1: Python Foundations for FastAPI

---

## Chapter 1: Python Fundamentals

### 1. Introduction
Python is a dynamic, high-level, interpreted language designed for readability and developer productivity. In modern backend engineering, understanding Python's core runtime behavior, variable reference models, and memory model (garbage collection, reference counting) is critical for building performant and leak-free APIs.

### 2. Concept Explanation
* **Why it exists**: Python was created to provide a highly readable, expressive language that balances speed of development with powerful abstractions.
* **When to use it**: Building web services, data processing systems, microservices, and AI integrations.
* **When NOT to use it**: For low-level system kernels, highly compute-intensive sub-millisecond latency trading engines (where C++/Rust/Go are preferred).
* **Advantages**: Expressive syntax, vast ecosystem, dynamic typing, automatic memory management.
* **Disadvantages**: Execution speed is slower compared to compiled languages; CPU-bound operations are historically restricted by the Global Interpreter Lock (GIL) (though Python 3.13 introduces experimental free-threaded builds).
* **Industry Use Cases**: Backend web servers, Machine Learning models deployment, automated scripts, ETL data pipelines.

### 3. Architecture Explanation
Python compiles source code (`.py`) into bytecode (`.pyc`), which is executed by the Python Virtual Machine (PVM). Objects are allocated on the heap, and variables are references pointing to these objects.
```
[Source Code .py] ---> [Compiler] ---> [Bytecode .pyc] ---> [PVM (Python Virtual Machine)]
```

### 4. Visual Workflow
```
+------------------+         +--------------------+
|  Variable (Name) | ------> | Heap Object (Value)|
|  e.g., user_id   |         | Type: Int, Ref: 1  |
+------------------+         +--------------------+
```

### 5. Real-World Scenario
An API endpoint needs to process an incoming list of transaction values. Modifying the list in-place versus returning a new copy can cause bugs if other parts of the application share a reference to that list.

### 6. Step-by-Step Implementation
1. Install Python 3.13.
2. Initialize a script to demonstrate object mutability and identity references.

### 7. Source Code Examples
```python
# demonstrate reference and memory allocation
def process_data():
    original_list = [10, 20, 30]
    referenced_list = original_list
    copied_list = list(original_list)
    
    referenced_list.append(40)
    
    print(f"Original: {original_list} (ID: {id(original_list)})")
    print(f"Referenced: {referenced_list} (ID: {id(referenced_list)})")
    print(f"Copied: {copied_list} (ID: {id(copied_list)})")

if __name__ == "__main__":
    process_data()
```

### 8. API Testing Examples
Verify the outputs in terminal:
```bash
python process_data.py
# Output:
# Original: [10, 20, 30, 40] (ID: 1407...)
# Referenced: [10, 20, 30, 40] (ID: 1407...)
# Copied: [10, 20, 30] (ID: 1408...)
```

### 9. Common Mistakes
Modifying mutable default arguments:
```python
def add_to_cart(item, cart=[]):  # MISTAKE: cart is shared across all calls!
    cart.append(item)
    return cart
```

### 10. Best Practices
Use `None` as the default value for mutable arguments:
```python
def add_to_cart(item, cart=None):
    if cart is None:
        cart = []
    cart.append(item)
    return cart
```

### 11. Interview Questions
* **Q: Explain the difference between `is` and `==` in Python.**
  * *A*: `==` checks for value equality (invoking `__eq__`), while `is` checks for identity equality (verifying if both references point to the exact same memory address using `id()`).

### 12. Chapter Summary
Python manages memory automatically via reference counting and garbage collection. Understanding mutability prevents unintended side-effects across shared state in concurrent execution environments.

### 13. Practice Exercises
Write a script that detects whether two variables containing nested lists reference the same sub-lists.

---

## Chapter 2: OOP Concepts

### 1. Introduction
Object-Oriented Programming (OOP) organizes code around objects and classes. FastAPI heavily utilizes OOP in Pydantic models, Custom Dependencies, and Database Models.

### 2. Concept Explanation
* **Why it exists**: OOP allows engineers to model real-world domains, encapsulate logic, inherit behavior, and enforce polymorphisism.
* **When to use it**: When building data structures, abstracting database tables (ORMs), or building custom service classes (e.g., email dispatchers, database repositories).
* **When NOT to use it**: For simple functional scripts, mathematical computations, or stateless pure operations.
* **Advantages**: Reusability, encapsulation, maintainability.
* **Disadvantages**: Can introduce unnecessary complexity and cognitive load if over-architected.
* **Industry Use Cases**: ORM model declarations, domain-driven architecture design.

### 3. Architecture Explanation
We use classes to represent entities and encapsulation to shield variables from external modification, exposing methods to execute verified mutations.
```
+-----------------------------------+
|              Class                |
| - attributes (private/__/public)  |
| - methods                         |
+-----------------------------------+
```

### 4. Visual Workflow
```
[Base Service] ---> [Auth Service] ---> [User Instance]
```

### 5. Real-World Scenario
An E-commerce API requires defining different user permissions and action boundaries (Customer, Administrator).

### 6. Step-by-Step Implementation
Define an abstract base base service and concrete subclasses implementing authorization hooks.

### 7. Source Code Examples
```python
from abc import ABC, abstractmethod

class BaseUser(ABC):
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    @abstractmethod
    def get_role(self) -> str:
        pass

class AdminUser(BaseUser):
    def get_role(self) -> str:
        return "Administrator"

class CustomerUser(BaseUser):
    def get_role(self) -> str:
        return "Customer"
```

### 8. API Testing Examples
```python
admin = AdminUser("alice", "alice@corp.com")
print(admin.get_role())  # Administrator
```

### 9. Common Mistakes
Using multiple inheritance without understanding Method Resolution Order (MRO), leading to unpredictable constructor executions.

### 10. Best Practices
Prefer composition over inheritance where possible. Keep inheritance hierarchies shallow (max 2–3 levels).

### 11. Interview Questions
* **Q: What is Method Resolution Order (MRO) in Python?**
  * *A*: MRO is the order in which Python searches for a method or attribute in a class hierarchy. Python uses the C3 Linearization algorithm to determine this order, which can be viewed using the `__mro__` attribute.

### 12. Chapter Summary
Encapsulation and polymorphism provide the blueprint for clean design. FastAPI leverages class inheritance for Pydantic models (`BaseModel`) and SQLAlchemy schemas.

### 13. Practice Exercises
Implement a class hierarchy representing a payment processor supporting Credit Cards and PayPal.

---

## Chapter 3: Decorators

### 1. Introduction
Decorators wrap functions or classes to modify or extend their behavior without altering the actual source code.

### 2. Concept Explanation
* **Why it exists**: To avoid repeating cross-cutting concerns (logging, authentication, timing, caching).
* **When to use it**: Defining route endpoints (`@app.get`), authenticating API keys, or logging execution time.
* **When NOT to use it**: For logic that is highly central to the core business algorithm and changes frequently.
* **Advantages**: Clean code separation, readability, modularity.
* **Disadvantages**: Can make debugging stack traces harder if wrappers are not implemented cleanly.
* **Industry Use Cases**: Routing in web frameworks, metric tracking, performance audits.

### 3. Architecture Explanation
A decorator takes a target function, wraps it inside an internal function that executes custom hooks, and returns the wrapper.
```
Client Request ---> [Decorator Wrapper: Checks Auth] ---> [Target Function]
```

### 4. Visual Workflow
```
+---------------------------------------------+
| Decorator                                   |
|   +-------------------------------------+   |
|   | Wrapper (Logs latency)              |   |
|   |   [Target Function Called]          |   |
|   +-------------------------------------+   |
+---------------------------------------------+
```

### 5. Real-World Scenario
An API developer needs to track and log execution latency for database-heavy operations.

### 6. Step-by-Step Implementation
Build a decorator that measures execution duration using Python's `time` module and logs it.

### 7. Source Code Examples
```python
import functools
import time
import logging

logging.basicConfig(level=logging.INFO)

def log_execution_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        logging.info(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@log_execution_time
def fetch_user_data(user_id: int):
    time.sleep(0.5)  # simulate DB query
    return {"id": user_id, "name": "John Doe"}
```

### 8. API Testing Examples
```python
fetch_user_data(42)
# Output in log: INFO:root:Function fetch_user_data took 0.5002 seconds
```

### 9. Common Mistakes
Forgetting to use `@functools.wraps(func)`, which erases the metadata (docstring, name) of the decorated function.

### 10. Best Practices
Always apply `@functools.wraps` to the inner wrapper function. Keep decorators lightweight.

### 11. Interview Questions
* **Q: Why should you use `functools.wraps`?**
  * *A*: `functools.wraps` copies the original function's name, docstring, and module attributes to the wrapper function, making it easier to debug and preserve introspection.

### 12. Chapter Summary
Decorators run code before and after a decorated function. FastAPI uses routing decorators to register path operations with the ASGI router.

### 13. Practice Exercises
Write a decorator that limits the execution of a function to 3 retries if an exception is raised.

---

## Chapter 4: Async Programming

### 1. Introduction
Asynchronous programming is the cornerstone of FastAPI's performance. It allows single-threaded execution environments to handle concurrent IO operations efficiently.

### 2. Concept Explanation
* **Why it exists**: Traditional synchronous systems block the execution thread while waiting for IO (database, network, file read), wasting CPU cycles. Async releases control back to the event loop.
* **When to use it**: Network operations, database calls, API integrations.
* **When NOT to use it**: CPU-bound tasks (e.g., image processing, heavy computation) where blocking occurs inside Python, starving the event loop.
* **Advantages**: High concurrency, minimal memory footprint per connection.
* **Disadvantages**: Requires non-blocking libraries (e.g., `httpx` instead of `requests`, `asyncpg` instead of `psycopg2`). Debugging is more complex.
* **Industry Use Cases**: High-throughput web gateways, real-time messaging, WebSockets.

### 3. Architecture Explanation
The Event Loop polls registered tasks. When a task reaches an `await` statement on a non-blocking operation, it yields control back to the loop, which executes other pending tasks.
```
+-------------------------------------------------------------+
|                         Event Loop                          |
|  [Task 1 (Waiting IO)]  --->  [Task 2 (Active)]  ---> etc.  |
+-------------------------------------------------------------+
```

### 4. Visual Workflow
```
Time Line:
Thread: [ Task 1 ... (Await IO) ] ===> [ Task 2 Running ] ===> [ Task 1 Resumes ]
```

### 5. Real-World Scenario
An API needs to make 3 independent external HTTP calls. Running them synchronously takes `T1 + T2 + T3`. Running them asynchronously takes `max(T1, T2, T3)`.

### 6. Step-by-Step Implementation
1. Use `asyncio` to execute tasks concurrently.
2. Build an async function simulating HTTP requests.

### 7. Source Code Examples
```python
import asyncio
import time

async def fetch_api_data(service_name: str, delay: float):
    print(f"Requesting {service_name}...")
    await asyncio.sleep(delay)  # Non-blocking IO wait
    print(f"Received response from {service_name}!")
    return {service_name: "success"}

async def main():
    start_time = time.perf_counter()
    results = await asyncio.gather(
        fetch_api_data("UserAuth", 1.5),
        fetch_api_data("ProductCatalog", 2.0),
        fetch_api_data("Inventory", 1.0)
    )
    end_time = time.perf_counter()
    print(f"All operations finished in {end_time - start_time:.2f}s")
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 8. API Testing Examples
```bash
python async_demo.py
# Output:
# Requesting UserAuth...
# Requesting ProductCatalog...
# Requesting Inventory...
# Received response from Inventory!
# Received response from UserAuth!
# Received response from ProductCatalog!
# All operations finished in 2.00s
```

### 9. Common Mistakes
Using blocking operations (like `time.sleep()` or synchronous database libraries) inside async functions. This blocks the entire thread and freezes the event loop.

### 10. Best Practices
Ensure all IO operations in an async endpoint are non-blocking. If a synchronous library must be used, delegate it to a thread pool via `run_in_executor`.

### 11. Interview Questions
* **Q: What is the difference between `async def` and regular `def` in FastAPI?**
  * *A*: `async def` defines a coroutine function that FastAPI schedules directly on the ASGI server's event loop. Regular `def` functions are run in an external thread pool by FastAPI to prevent blocking the event loop.

### 12. Chapter Summary
Asynchronous programming unlocks high throughput. Event loop concurrency ensures you can handle thousands of connections on a single process.

### 13. Practice Exercises
Write an async script that calls 5 public APIs concurrently and aggregates their results, handling timeouts using `asyncio.wait_for`.

---

## Chapter 5: Type Hinting

### 1. Introduction
Type Hinting enables static code analysis, validation, and auto-generated API specifications in FastAPI.

### 2. Concept Explanation
* **Why it exists**: Python is dynamically typed. Type hints clarify what parameters a function expects, allowing editors to autocomplete and linters to spot errors.
* **When to use it**: Everywhere in FastAPI. Paths, query params, and request models require explicit type declarations.
* **When NOT to use it**: Throwaway prototype scripts (though still recommended).
* **Advantages**: Code reliability, autocomplete, self-documenting code.
* **Disadvantages**: Slight syntax verbosity.
* **Industry Use Cases**: Pydantic schemas, compile-time checks, type-driven API generation.

### 3. Architecture Explanation
FastAPI inspects type hints at runtime via Python's reflection system (`__annotations__`) to build Pydantic validation schemas.
```
Type Hints (int, str) ---> Pydantic (Parses & Validates) ---> OpenAPI JSON Spec
```

### 4. Visual Workflow
```
User Payload: {"age": "25"} ---> FastAPI checks hint (int) ---> Casts to 25 ---> App Logic
```

### 5. Real-World Scenario
An endpoint must receive an integer ID. If a user passes a string, the system should catch the error before executing query logic.

### 6. Step-by-Step Implementation
Define typing constructs using Python 3.13 syntax.

### 7. Source Code Examples
```python
def process_user_id(user_id: int, tags: list[str]) -> str:
    # Python 3.13 uses native list[str] instead of typing.List[str]
    return f"User ID: {user_id}, Tags: {', '.join(tags)}"

if __name__ == "__main__":
    result = process_user_id(101, ["admin", "premium"])
    print(result)
```

### 8. API Testing Examples
Verify typing static checks using `mypy`:
```bash
mypy script.py
# Success: no issues found
```

### 9. Common Mistakes
Declaring generic collections with deprecated capital-letter types (`typing.List`, `typing.Dict`) instead of standard built-ins (`list`, `dict`) in modern Python.

### 10. Best Practices
Use native types (`list[str]`, `dict[str, int]`) and union operators (`str | None`) available in modern Python versions.

### 11. Interview Questions
* **Q: How does FastAPI use Python type hints at runtime?**
  * *A*: FastAPI reads function signatures and their type annotations to validate incoming query/path parameters, generate response models, and construct the Swagger UI schema.

### 12. Chapter Summary
Type hinting is not just documentation; in FastAPI, it acts as the validation schema driver.

### 13. Practice Exercises
Create a function that processes a union type of `dict` or `list`, type hinted appropriately, and analyze it with `mypy`.

---

## Chapter 6: Generators

### 1. Introduction
Generators provide a memory-efficient way to process large data collections iteratively without loading them fully into RAM.

### 2. Concept Explanation
* **Why it exists**: Loading a million database records into memory causes out-of-memory errors. Generators yield items one at a time.
* **When to use it**: Streaming log files, pagination, database cursors.
* **When NOT to use it**: When random access is needed (like reading the 100th element directly without reading the first 99).
* **Advantages**: Memory efficiency, lazy evaluation.
* **Disadvantages**: Single-pass traversal only; cannot be indexed or sliced.
* **Industry Use Cases**: Database streaming, streaming HTTP responses.

### 3. Architecture Explanation
Generators suspend execution using the `yield` keyword, saving state between iterations.
```
Caller ---> next() ---> Generator (executes to yield) ---> returns value ---> Suspends
```

### 4. Visual Workflow
```
[Client] <--- (Yield Item 1) --- [ Generator ] <--- (Read Chunk 1 from Disk)
[Client] <--- (Yield Item 2) --- [ Generator ] <--- (Read Chunk 2 from Disk)
```

### 5. Real-World Scenario
An API needs to export a CSV containing 500,000 transaction records.

### 6. Step-by-Step Implementation
Create a generator that simulates chunked retrieval of transaction data.

### 7. Source Code Examples
```python
import time

def get_large_transactions(limit: int):
    for i in range(1, limit + 1):
        time.sleep(0.01)  # Simulating DB latency
        yield {"id": i, "amount": i * 10.5, "status": "processed"}

if __name__ == "__main__":
    # Consume memory-efficient generator
    for transaction in get_large_transactions(5):
        print(transaction)
```

### 8. API Testing Examples
Ensure items yield sequentially:
```bash
python generator.py
# Prints items one by one with a delay
```

### 9. Common Mistakes
Exhausting a generator and attempting to iterate over it again (it will remain empty).

### 10. Best Practices
Use generators for reading large files or streaming queries. Do not cast generators to lists unless necessary.

### 11. Interview Questions
* **Q: What is the difference between `yield` and `return`?**
  * *A*: `return` exits the function completely, destroying local variables. `yield` pauses the function, returning a value to the caller, and retains its stack frame for resumption.

### 12. Chapter Summary
Generators are core to processing pipelines. In FastAPI, generator-based dependencies allow running cleanup logic after returning a response.

### 13. Practice Exercises
Write a generator that streams logs from a text file, filtering for lines containing "ERROR".

---

## Chapter 7: Context Managers

### 1. Introduction
Context managers guarantee clean initialization and teardown of external resources (like databases or files), even if errors occur during execution.

### 2. Concept Explanation
* **Why it exists**: Manual resource management (opening and explicitly closing connections) is prone to leaks if an exception is raised.
* **When to use it**: Managing database connections, file handles, lock acquisitions.
* **When NOT to use it**: For state mutations that don't involve external resources or setup/teardown processes.
* **Advantages**: Prevents leaks, enforces clean code structures.
* **Disadvantages**: Adds an indentation level (`with` statement).
* **Industry Use Cases**: Session management, transactional locks.

### 3. Architecture Explanation
Context managers implement the protocols `__enter__` and `__exit__`. Async context managers implement `__aenter__` and `__aexit__`.
```
with Context() ---> __enter__ ---> [ Block Code Executing ] ---> __exit__ (closes resource)
```

### 4. Visual Workflow
```
+------------------------------------+
|  __enter__ (Create Connection)     |
|     +-------------------------+    |
|     |  Your Code Executes     |    |
|     +-------------------------+    |
|  __exit__ (Ensure connection closed)|
+------------------------------------+
```

### 5. Real-World Scenario
An API endpoint needs to write a temp file, read it, and ensure it is deleted afterwards.

### 6. Step-by-Step Implementation
Implement an async context manager managing a mock database transaction.

### 7. Source Code Examples
```python
import asyncio
from contextlib import asynccontextmanager

class MockDBConnection:
    async def connect(self):
        print("Database Connected.")
    async def close(self):
        print("Database Disconnected.")

@asynccontextmanager
async def database_session():
    db = MockDBConnection()
    await db.connect()
    try:
        yield db
    finally:
        await db.close()

async def main():
    async with database_session() as session:
        print("Running database queries...")

if __name__ == "__main__":
    asyncio.run(main())
```

### 8. API Testing Examples
```bash
python context_demo.py
# Output:
# Database Connected.
# Running database queries...
# Database Disconnected.
```

### 9. Common Mistakes
Forgetting to handle exceptions inside the generator/context manager, preventing correct teardown execution.

### 10. Best Practices
Always wrap yielding sections in context managers in `try/finally` blocks to guarantee cleanup logic runs.

### 11. Interview Questions
* **Q: How does `async with` differ from `with` in Python?**
  * *A*: `async with` invokes `__aenter__` and `__aexit__`, which are coroutine methods, allowing the event loop to switch tasks during initialization and cleanup operations.

### 12. Chapter Summary
Context managers are crucial to prevent resource leaks. In FastAPI, `dependencies` with `yield` are translated internally into context managers.

### 13. Practice Exercises
Write a context manager that records the total time spent executing code block operations and writes it to a file.

---

## Chapter 8: Dataclasses

### 1. Introduction
Python dataclasses automate boilerplate setups (like constructors, representations, and equality tests) for data containers.

### 2. Concept Explanation
* **Why it exists**: Defining simple state models manually requires writing redundant `__init__`, `__repr__`, and `__eq__` methods.
* **When to use it**: In-memory domain objects, configurations, structures that don't require external parsing/validation (for API requests, Pydantic is preferred).
* **When NOT to use it**: Validating external payloads (FastAPI/Pydantic schemas should be used instead).
* **Advantages**: Clean declarations, built-in ordering and immutability options (`frozen=True`).
* **Disadvantages**: Lacks built-in parsing and rigorous coercion compared to Pydantic.
* **Industry Use Cases**: Internal state representation, config structures.

### 3. Architecture Explanation
The `@dataclass` decorator inspects annotations to inject methods into class definitions.
```
@dataclass
class User ---> Metaprogramming ---> Injects __init__, __repr__, __eq__
```

### 4. Visual Workflow
```
[UserDefinition (Dataclass)] ---> Injects default constructs ---> Instantiation
```

### 5. Real-World Scenario
Defining an internal tracking event structure in an application before emitting it to a message broker.

### 6. Step-by-Step Implementation
Define a dataclass with default factory parameters.

### 7. Source Code Examples
```python
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class AnalyticEvent:
    event_name: str
    payload: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

if __name__ == "__main__":
    event = AnalyticEvent(event_name="user_login", payload={"user_id": 99})
    print(event)
```

### 8. API Testing Examples
Verify instantiation and representation output:
```bash
python dataclass_demo.py
# Output: AnalyticEvent(event_name='user_login', payload={'user_id': 99}, timestamp=datetime.datetime(...))
```

### 9. Common Mistakes
Passing a mutable collection (`list`, `dict`) directly as a default value, leading to shared state errors (use `field(default_factory=...)` instead).

### 10. Best Practices
Use `frozen=True` for structures that should remain read-only. Use `default_factory` for mutable fields.

### 11. Interview Questions
* **Q: How do you declare a mutable default in a dataclass?**
  * *A*: You must use `field(default_factory=list)` (or `dict`/etc.) so that a new instance is created for each object.

### 12. Chapter Summary
Dataclasses are ideal for modeling internal system domain components, complementing Pydantic's verification layer.

### 13. Practice Exercises
Define a frozen dataclass representing a static server configuration.

---

## Chapter 9: Typing Module

### 1. Introduction
The `typing` module enables rich static annotations, facilitating type checks and API contracts in enterprise Python applications.

### 2. Concept Explanation
* **Why it exists**: Basic type hints are insufficient for complex constructs (generic databases, callable functions, protocols).
* **When to use it**: Defining interfaces, type parameters, variable parameters, database models.
* **When NOT to use it**: Simple operations with basic primitive structures.
* **Advantages**: Support for complex typing constraints (Generics, TypeVar, Protocols).
* **Disadvantages**: Syntactic complexity.
* **Industry Use Cases**: Designing generic base database repositories.

### 3. Architecture Explanation
Typing classes are used during lint checks (`mypy`) and are discarded at runtime (no performance degradation).
```
[Type Annotation Code] ---> Checked by Mypy ---> Stripped out at Execution
```

### 4. Visual Workflow
```
Type Checker: TypeVar(T) ---> generic_func(T) ---> verifies inputs match outputs
```

### 5. Real-World Scenario
Creating a generic base service that fetches records from different collections while preserving model types.

### 6. Step-by-Step Implementation
Define a generic repository interface using Python 3.13 standard typing parameters.

### 7. Source Code Examples
```python
from typing import Generic, TypeVar

# T stands for the database model
T = TypeVar('T')

class GenericRepository(Generic[T]):
    def __init__(self):
        self._db: list[T] = []

    def add(self, entity: T) -> None:
        self._db.append(entity)

    def get_all(self) -> list[T]:
        return self._db

class Invoice:
    def __init__(self, amount: float):
        self.amount = amount

if __name__ == "__main__":
    repo = GenericRepository[Invoice]()
    repo.add(Invoice(250.0))
    print(repo.get_all()[0].amount)
```

### 8. API Testing Examples
Validate the script logic with `mypy`:
```bash
mypy generic_repo.py
# Success: no issues found
```

### 9. Common Mistakes
Assuming typing validates values at runtime (typing only annotations; validations require frameworks like Pydantic).

### 10. Best Practices
Use `Protocol` to define structural subtyping (duck typing interfaces). Use PEP 695 type parameters where supported by your target python environment.

### 11. Interview Questions
* **Q: What is the purpose of `typing.Protocol`?**
  * *A*: `Protocol` is used for structural subtyping. Classes that implement the methods defined in a Protocol class are automatically considered subtypes, without inheriting from it.

### 12. Chapter Summary
The typing system enables robust, auto-complete enabled, testable enterprise APIs.

### 13. Practice Exercises
Implement a generic message parser supporting multiple formats using `typing.Generic`.
