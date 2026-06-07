# Part 23: End-to-End Projects

This section presents the full architectures, folder structures, database designs, API endpoints, source code foundations, testing patterns, and deployment configurations for 10 complete systems.

---

## Project 1: Student Management System

### 1. Architecture & Folder Structure
```
student_system/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── routes.py
├── tests/
│   └── test_students.py
├── Dockerfile
└── docker-compose.yml
```

### 2. Database Design
* **Table**: `students`
  * `id`: Integer (PK, autoincrement)
  * `name`: String (not null)
  * `email`: String (unique, index)
  * `age`: Integer
  * `enrolled_class`: String

### 3. API Endpoints
* `POST /students` - Register a student
* `GET /students/{id}` - Get student profile
* `GET /students` - Paginated student list

### 4. Source Code
```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Student Management System")
SQLALCHEMY_DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB Model
class StudentModel(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)

Base.metadata.create_all(bind=engine)

# Schemas
class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    age: int

class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int
    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(StudentModel).filter(StudentModel.email == student.email).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_student = StudentModel(name=student.name, email=student.email, age=student.age)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student
```

### 5. Testing
```python
# tests/test_students.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_student():
    response = client.post("/students", json={"name": "Alice", "email": "alice@school.com", "age": 20})
    assert response.status_code == 201
    assert response.json()["email"] == "alice@school.com"
```

### 6. Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
```

---

## Project 2: Employee Management System

### 1. Architecture & Folder Structure
```
employee_system/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   └── routes/
│       ├── employees.py
│       └── departments.py
```

### 2. Database Design
* **Table**: `departments` (id [PK], name)
* **Table**: `employees` (id [PK], name, email, department_id [FK])

### 3. API Endpoints
* `POST /departments` - Create department
* `POST /employees` - Add employee with department reference
* `GET /departments/{id}/employees` - Get all employees in a department

### 4. Source Code
```python
# app/main.py (Summary setup)
from fastapi import FastAPI
from app.routes import employees, departments

app = FastAPI(title="Employee Management")
app.include_router(employees.router)
app.include_router(departments.router)
```

---

## Project 3: Library Management API

### 1. Architecture & Folder Structure
```
library_system/
├── app/
│   ├── main.py
│   ├── models.py
│   └── schemas.py
```

### 2. Database Design
* **Table**: `books` (id [PK], title, author, isbn, available_copies)
* **Table**: `borrow_records` (id [PK], book_id [FK], borrower_name, return_date)

### 3. API Endpoints
* `POST /books` - Catalog new book
* `POST /books/{id}/borrow` - Rent a copy
* `POST /books/{id}/return` - Return a copy

### 4. Source Code
```python
# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Library Management API")

class Book(BaseModel):
    id: int
    title: str
    available_copies: int

BOOKS_DB = {
    1: Book(id=1, title="FastAPI Mastery", available_copies=3)
}

@app.post("/books/{book_id}/borrow")
def borrow_book(book_id: int):
    book = BOOKS_DB.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No copies available")
    book.available_copies -= 1
    return {"message": "Success", "remaining_copies": book.available_copies}
```

---

## Project 4: Expense Tracker

### 1. Architecture & Folder Structure
```
expense_tracker/
├── app/
│   ├── main.py
│   └── tracker.py
```

### 2. Database Design
* **Table**: `expenses` (id [PK], category, amount, date, description)

### 3. API Endpoints
* `POST /expenses` - Add expense
* `GET /expenses/summary` - Total expenses grouped by category
* `DELETE /expenses/{id}` - Delete transaction

### 4. Source Code
```python
# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Expense Tracker")

class Expense(BaseModel):
    category: str
    amount: float

EXPENSES = []

@app.post("/expenses")
def add_expense(expense: Expense):
    EXPENSES.append(expense)
    return {"status": "added", "expense": expense}

@app.get("/expenses/summary")
def get_summary():
    summary = {}
    for exp in EXPENSES:
        summary[exp.category] = summary.get(exp.category, 0.0) + exp.amount
    return summary
```

---

## Project 5: Blogging Platform

### 1. Architecture & Folder Structure
```
blog_platform/
├── app/
│   ├── main.py
│   ├── database.py
│   └── routes.py
```

### 2. Database Design (NoSQL MongoDB)
* **Collection**: `posts`
  * `_id`: ObjectId
  * `title`: String
  * `content`: String
  * `comments`: Array of objects [author, text, date]

### 3. API Endpoints
* `POST /posts` - Publish post
* `POST /posts/{id}/comments` - Add comment
* `GET /posts` - List posts

### 4. Source Code
```python
# app/main.py (MongoDB mock CRUD)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Blogging Platform")

class Post(BaseModel):
    title: str
    content: str

POSTS = []

@app.post("/posts")
def create_post(post: Post):
    POSTS.append(post)
    return {"message": "Published", "post": post}
```

---

## Project 6: E-Commerce Backend

### 1. Architecture & Folder Structure
```
ecommerce_backend/
├── app/
│   ├── main.py
│   ├── checkout.py
│   └── inventory.py
```

### 2. Database Design
* **Table**: `products` (id [PK], name, price, stock)
* **Table**: `orders` (id [PK], total_price, status)

### 3. API Endpoints
* `POST /cart/checkout` - Secure order creation
* `GET /products` - List products in inventory
* `PUT /products/{id}/stock` - Update inventory levels

### 4. Source Code
```python
# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="E-Commerce API")

class CheckoutItem(BaseModel):
    product_id: int
    quantity: int

PRODUCTS = {1: {"name": "Mug", "price": 10.0, "stock": 5}}

@app.post("/cart/checkout")
def checkout(item: CheckoutItem):
    prod = PRODUCTS.get(item.product_id)
    if not prod or prod["stock"] < item.quantity:
        raise HTTPException(status_code=400, detail="Item out of stock")
    prod["stock"] -= item.quantity
    return {"status": "Order Complete", "total": prod["price"] * item.quantity}
```

---

## Project 7: JWT Authentication Service

### 1. Architecture & Folder Structure
```
jwt_service/
├── app/
│   ├── main.py
│   ├── auth.py
│   └── security.py
```

### 2. Database Design
* **Table**: `users` (id [PK], username, email, hashed_password)

### 3. API Endpoints
* `POST /auth/register` - Create user with hashed password
* `POST /auth/token` - Get JWT access token
* `GET /auth/verify` - Validate token

### 4. Source Code
See **Part 6: Authentication & Security** for the complete, production-ready enterprise implementation of the JWT service.

---

## Project 8: Resume Upload Portal

### 1. Architecture & Folder Structure
```
upload_portal/
├── app/
│   ├── main.py
│   └── storage.py
```

### 2. Storage Design
* Uploaded files are saved to `uploads/` directory on server disk, validated by MIME extension, and mapped to user databases.

### 3. API Endpoints
* `POST /resumes/upload` - Secure PDF multipart upload
* `GET /resumes/{filename}` - Retrieve file

### 4. Source Code
```python
# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil

app = FastAPI(title="Resume Portal")

@app.post("/resumes/upload")
async def upload(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDFs allowed")
    
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "saved"}
```

---

## Project 9: AI Resume Analyzer

### 1. Architecture & Folder Structure
```
resume_analyzer/
├── app/
│   ├── main.py
│   └── ai.py
```

### 2. AI Integration Design
* Extracted text is sent to the OpenAI/Gemini API using RAG embeddings to query experience metrics.

### 3. API Endpoints
* `POST /analyze` - Parse uploaded text and generate LLM summaries
* `POST /query` - Ask candidate compatibility questions

### 4. Source Code
See **Part 21: LLM Applications** for the complete, production-ready implementation of the AI Resume Analyzer.

---

## Project 10: Enterprise Microservices Platform

### 1. Architecture & Folder Structure
```
microservices/
├── gateway/
│   └── main.py
├── order_service/
│   └── main.py
├── inventory_service/
│   └── main.py
└── docker-compose.yml
```

### 2. Event Routing Design
* Client connects to API Gateway. API Gateway routes requests to specific microservice instances. Microservices sync state asynchronously via Redis streams.

### 3. API Endpoints
* `POST /gateway/orders/checkout` -> Routes to Order microservice
* `GET /gateway/inventory/status` -> Routes to Inventory microservice

### 4. Source Code
See **Part 22: Microservices** for the complete, production-ready implementation of the gateway and order routing systems.
