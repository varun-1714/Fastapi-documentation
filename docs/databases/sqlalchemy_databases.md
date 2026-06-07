# Part 7: Databases (SQLAlchemy 2.0)

---

## Chapter 1: SQLAlchemy 2.0 Async Setup & Employee DB Model

### 1. Introduction
Relational databases are the standard choice for data persistence in enterprise applications. SQLAlchemy 2.0 is Python's leading SQL toolkit and Object Relational Mapper (ORM), featuring native async execution models and strict typing.

### 2. Concept Explanation
* **Why it exists**: An ORM maps database tables to Python classes, allowing developers to query and manipulate data using Python code instead of writing raw SQL strings.
* **When to use it**: Relational data models, complex table joins, transaction-heavy systems.
* **When NOT to use it**: Highly unstructured document data (where NoSQL like MongoDB is preferred) or simple caching layers (where Redis is preferred).
* **Advantages**: Typed model definitions, database independence (supports PostgreSQL, MySQL, SQLite), automatic migrations with Alembic, prevention of SQL injection.
* **Disadvantages**: Can introduce performance overhead on complex query plans compared to optimized raw SQL.
* **Industry Use Cases**: Enterprise ERPs, banking ledgers, user profile datastores.

### 3. Architecture Explanation
The architecture uses a modern asynchronous engine that coordinates connections, maps models using `DeclarativeBase`, and processes transactions through scoped async sessions.
```
FastAPI Router ---> AsyncSession ---> AsyncEngine ---> Database (e.g. PostgreSQL)
```

### 4. Visual Workflow
```
[Client Call] ---> [Route Handler] ---> [get_db Session] ---> [Executes Async Query] ---> [Commit DB]
```

### 5. Real-World Scenario
An HR department needs a backend API to manage company department structures and employee details, requiring foreign key constraints and transactional integrity.

### 6. Step-by-Step Implementation
1. Install databases packages: `sqlalchemy[asyncio]`, `asyncpg` (PostgreSQL driver).
2. Configure the async engine and session factory.
3. Define the database models for `Department` and `Employee` with one-to-many relationships.

### 7. Source Code Examples
```python
import asyncio
from typing import List
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Database Connection URI (SQLite async driver for portable execution)
DATABASE_URL = "sqlite+aiosqlite:///./company.db"

# Declare Declarative Base
class Base(DeclarativeBase):
    pass

# Models
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # One-to-many relationship
    employees: Mapped[List["Employee"]] = relationship(
        back_populates="department", cascade="all, delete-orphan"
    )

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)

    # Relationship back to department
    department: Mapped["Department"] = relationship(back_populates="employees")

# Async Engine and Session
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Dependency to get session context
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 8. API Testing Examples
Verify model initialization and insertions:
```python
async def init_db_and_insert():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Insert Department
        hr_dept = Department(name="HR")
        session.add(hr_dept)
        await session.flush()  # populate hr_dept.id

        # Insert Employee
        new_emp = Employee(name="Jane Doe", email="jane@company.com", department_id=hr_dept.id)
        session.add(new_emp)
        await session.commit()
        print("Database initialized and mock data inserted.")

if __name__ == "__main__":
    asyncio.run(init_db_and_insert())
```

### 9. Common Mistakes
Forgetting to use `await` with SQLAlchemy async queries (e.g. executing `session.execute()` synchronously), resulting in unresolved coroutine warnings.

### 10. Best Practices
Always set `expire_on_commit=False` on `async_sessionmaker` to prevent SQLAlchemy from attempting to execute blocking queries when accessing model attributes after a transaction commits.

### 11. Interview Questions
* **Q: Why is `expire_on_commit=False` recommended in SQLAlchemy async setups?**
  * *A*: By default, committing a transaction expires all object attributes, forcing SQLAlchemy to lazy-load them on subsequent access. In an async application, accessing these expired attributes will trigger blocking synchronous database queries, raising an error or freezing the event loop.

### 12. Chapter Summary
SQLAlchemy 2.0 supports async database operations. Defining models using type annotations (`Mapped`, `mapped_column`) ensures code readability and type safety.

### 13. Practice Exercises
Add a salary column to the employee model and write an async query to fetch the average salary of employees in each department.

---

## Chapter 2: Database Migrations with Alembic

### 1. Introduction
As applications grow, their database schemas evolve. Alembic is SQLAlchemy's companion migration tool, allowing you to track and apply database schema changes over time.

### 2. Concept Explanation
* **Why it exists**: Modifying production database tables manually causes data drift and synchronization issues across dev and prod environments. Alembic automates schema updates.
* **When to use it**: Any project that connects to a database and needs to track and apply schema changes.
* **When NOT to use it**: Prototypes using temporary in-memory databases (where tables can simply be created on start).
* **Advantages**: Version control for database schemas, rollback support, autogeneration of migration files.
* **Disadvantages**: Auto-generated migrations require manual review to ensure they handle index modifications and column renames correctly.
* **Industry Use Cases**: Deploying database schema changes as part of a CI/CD pipeline.

### 3. Architecture Explanation
Alembic reads the database state, compares it with the metadata of your SQLAlchemy models, and generates migration files (`.py`) detailing the differences.
```
SQLAlchemy Models  <-- (Diff Engine) -->  Database State
                              |
                     [ Migration Script ]
```

### 4. Visual Workflow
```
Modify Model (e.g. add age) ---> alembic revision --autogenerate ---> alembic upgrade head
```

### 5. Real-World Scenario
An HR application needs to add a phone number field to the employee table without losing existing user records.

### 6. Step-by-Step Implementation
1. Install alembic: `pip install alembic`.
2. Initialize Alembic: `alembic init -t async migrations`.
3. Configure `migrations/env.py` to import SQLAlchemy model metadata.
4. Generate and run the migration.

### 7. Source Code Configuration Example
`migrations/env.py` (Relevant changes to make: import models and set `target_metadata`):
```python
# In migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import your Base model metadata here
from book.part_07_databases import Base
target_metadata = Base.metadata

# The rest of env.py handles executing migrations in async context
```

### 8. CLI Command Examples
Initialize migrations directory:
```bash
alembic init -t async migrations
```
Generate migration file comparing models and database:
```bash
alembic revision --autogenerate -m "add_phone_to_employee"
```
Apply migration to the target database:
```bash
alembic upgrade head
```

### 9. Common Mistakes
Forgetting to import the database models inside `env.py`, causing Alembic to generate blank migration scripts.

### 10. Best Practices
Always inspect auto-generated migrations manually before applying them to production databases.

### 11. Interview Questions
* **Q: How does Alembic track the current migration version of a database?**
  * *A*: Alembic creates a table named `alembic_version` in the database, containing a single row with the revision ID of the last applied migration.

### 12. Chapter Summary
Alembic enables database version control. Using auto-generated migration scripts ensures schemas are updated safely across environments.

### 13. Practice Exercises
Add a status field to the employee table, generate a migration script, verify the SQL commands generated, and apply the migration.
