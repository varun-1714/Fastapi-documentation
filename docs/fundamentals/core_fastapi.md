# Part 3: Core FastAPI

---

## Chapter 1: Routing & Parameters (Student API)

### 1. Introduction
Routing handles mapping incoming HTTP request URLs and methods to specific Python coroutines. FastAPI makes routing intuitive by supporting path and query parameter type coercion directly inside the route signature.

### 2. Concept Explanation
* **Why it exists**: To receive dynamic segments in a URL path (e.g., `/students/{id}`) or parameter filters (e.g., `/students?grade=A`) and convert them into Python variables.
* **When to use it**: When building endpoints querying specific database records by ID, or filtering collections.
* **When NOT to use it**: If payload objects are large, complex, or contain security credentials (use Request Body POST requests instead).
* **Advantages**: Seamless parameter coercion, automatic error generation for invalid types.
* **Disadvantages**: Heavy query parameter lists can clutter URLs.
* **Industry Use Cases**: Fetching customer records by UUID, filtering product searches.

### 3. Architecture Explanation
FastAPI parses route signatures, matching path tokens against URL variables, and matches remaining arguments against URL query strings.
```
Request URI: /students/105?grade=A
                  |        |
           Path Param     Query Param
```

### 4. Visual Workflow
```
Client Request ---> Router Matches Path ---> Casts '105' to int ---> Matches Query 'A' ---> Executes handler
```

### 5. Real-World Scenario
An educational institute needs an API to manage student records, allowing details to be retrieved by ID and filtered by grade or status.

### 6. Step-by-Step Implementation
1. Create a FastAPI router for student operations.
2. Implement endpoints for single student lookup and paginated listings.

### 7. Source Code Examples
```python
from fastapi import FastAPI, Path, Query, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Student API")

class Student(BaseModel):
    id: int
    name: str
    grade: str
    enrolled: bool

# In-memory database
STUDENTS_DB = {
    1: Student(id=1, name="Alice Smith", grade="A", enrolled=True),
    2: Student(id=2, name="Bob Jones", grade="B", enrolled=True),
    3: Student(id=3, name="Charlie Brown", grade="A", enrolled=False),
}

@app.get("/students/{student_id}", status_code=status.HTTP_200_OK)
async def get_student_by_id(
    student_id: int = Path(..., description="The ID of the student to retrieve", gt=0)
):
    student = STUDENTS_DB.get(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Student with ID {student_id} not found"
        )
    return student

@app.get("/students", status_code=status.HTTP_200_OK)
async def list_students(
    grade: str | None = Query(None, max_length=2, description="Filter students by grade"),
    limit: int = Query(10, ge=1, le=100)
):
    results = list(STUDENTS_DB.values())
    if grade:
        results = [s for s in results if s.grade == grade]
    return results[:limit]
```

### 8. API Testing Examples
Request a student by ID:
```bash
curl -X GET http://127.0.0.1:8000/students/1
# Response: {"id":1,"name":"Alice Smith","grade":"A","enrolled":true}
```
Query students by grade:
```bash
curl -X GET "http://127.0.0.1:8000/students?grade=A"
# Response: [{"id":1,"name":"Alice Smith","grade":"A","enrolled":true}, ...]
```

### 9. Common Mistakes
Failing to specify type validation limits (e.g., allowing negative integers as IDs).

### 10. Best Practices
Always use validation constraints like `gt=0` for IDs and `max_length` for string filters in `Path` and `Query`.

### 11. Interview Questions
* **Q: What is the difference between Path parameters and Query parameters?**
  * *A*: Path parameters are variable parts of the URL path required to identify a resource. Query parameters are optional key-value pairs appended after the `?` character, primarily used to filter, sort, or paginate results.

### 12. Chapter Summary
Path parameters locate resources, and query parameters filter them. FastAPI automatically parses both.

### 13. Practice Exercises
Add a path parameter `/students/{student_id}/status` that updates the enrollment state of the student.

---

## Chapter 2: Request Body & Response Models (Employee API)

### 1. Introduction
POST and PUT operations send payload data inside the HTTP request body. Defining response models ensures outgoing data is parsed and sensitive fields are excluded.

### 2. Concept Explanation
* **Why it exists**: Pydantic response models filter out internal database structures (like hashed passwords or private keys) before they reach client targets.
* **When to use it**: Every endpoint returning data to exclude internal attributes or format JSON responses.
* **When NOT to use it**: Endpoints returning raw binaries or static media files.
* **Advantages**: Automatic payload documentation, input data coercion, outbound schema serialization.
* **Disadvantages**: Running model conversions on thousands of fields introduces a minor serialization CPU overhead.
* **Industry Use Cases**: Sanitizing API payloads, returning formatted records.

### 3. Architecture Explanation
The request body is parsed into a Pydantic model. When returning data, the handler's output is validated against the declared `response_model`.
```
Payload JSON ---> Pydantic Request Model ---> Business Logic ---> Pydantic Response Model ---> Sanitized Output JSON
```

### 4. Visual Workflow
```
Client Send: {"name": "Alice", "ssn": "123-45"} ---> [ FastAPI Route ] ---> Response: {"name": "Alice"} (SSN hidden)
```

### 5. Real-World Scenario
An HR API manages employee profiles. When an employee is created or retrieved, internal fields like their salary and SSN must be hidden from normal user endpoints.

### 6. Step-by-Step Implementation
1. Define base, request, and response schemas.
2. Implement routing functions returning custom schemas.

### 7. Source Code Examples
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Employee API")

# Schemas
class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    salary: float  # Internal field
    ssn: str       # Sensitive field

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str

# In-memory database
EMPLOYEES_DB = {}
employee_id_counter = 1

@app.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(employee_in: EmployeeCreate):
    global employee_id_counter
    # Simulate DB entry saving salary and SSN internally
    db_entry = employee_in.model_dump()
    db_entry["id"] = employee_id_counter
    EMPLOYEES_DB[employee_id_counter] = db_entry
    employee_id_counter += 1
    return db_entry

@app.get("/employees/{emp_id}", response_model=EmployeeResponse)
async def get_employee(emp_id: int):
    employee = EMPLOYEES_DB.get(emp_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
```

### 8. API Testing Examples
Create employee:
```bash
curl -X POST http://127.0.0.1:8000/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@corp.com", "department": "Engineering", "salary": 95000.0, "ssn": "987-654-321"}'
# Response (Salary and SSN are filtered out):
# {"id":1,"name":"Jane Doe","email":"jane@corp.com","department":"Engineering"}
```

### 9. Common Mistakes
Returning database ORM objects directly without specifying a `response_model`, exposing sensitive columns.

### 10. Best Practices
Always define explicit input (`EmployeeCreate`) and output (`EmployeeResponse`) models to separate DB storage from presentation representations.

### 11. Interview Questions
* **Q: What is the benefit of declaring a `response_model` in route decorators?**
  * *A*: It automatically formats the response payload, excludes fields not defined in the model, provides validation checks on output data, and updates the Swagger UI schema document.

### 12. Chapter Summary
Request bodies receive payloads, and response models sanitize outgoing JSON responses.

### 13. Practice Exercises
Add a route to update an employee's department, using a dedicated `EmployeeUpdate` schema.

---

## Chapter 3: Request Inputs: Headers, Cookies, & Forms (Product API)

### 1. Introduction
APIs often receive inputs via HTTP headers (for metadata and tokens), cookies (for sessions), and HTML forms (for traditional file uploads).

### 2. Concept Explanation
* **Why it exists**: Custom headers pass authentication tokens and trace IDs. Cookies manage session states, and Forms handle URL-encoded post requests and binary uploads.
* **When to use it**: User logins, browser integrations, secure tokens.
* **When NOT to use it**: Standard REST payloads (where application/json request bodies are cleaner).
* **Advantages**: Adheres to browser standards, supports multipart streams.
* **Disadvantages**: Forms and cookies require manual validation compared to structured JSON.
* **Industry Use Cases**: CSRF validation tokens, secure session tracking.

### 3. Architecture Explanation
FastAPI extracts metadata fields from the HTTP request context and converts them using `Header`, `Cookie`, and `Form` utility functions.
```
Request ---> [Headers Parser] ---> Header("X-API-Key")
        ---> [Cookies Parser] ---> Cookie("session_id")
        ---> [Form Data]      ---> Form("product_name")
```

### 4. Visual Workflow
```
Client Request ---> [HTTP Header: X-Request-ID] ---> API Controller reads Header ---> Logs Trace ID
```

### 5. Real-World Scenario
A Product API needs to handle product registration via a form submit, accepting an optional authorization API key from custom headers and session tokens from cookies.

### 6. Step-by-Step Implementation
1. Import `Header`, `Cookie`, `Form`.
2. Construct product registration routes processing these inputs.

### 7. Source Code Examples
```python
from fastapi import FastAPI, Header, Cookie, Form, HTTPException, status

app = FastAPI(title="Product API")

@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product_via_form(
    x_api_key: str = Header(..., description="API Access Token"),
    session_id: str | None = Cookie(None, description="User Session Cookie"),
    name: str = Form(..., description="The name of the product"),
    price: float = Form(..., gt=0.0)
):
    # Authenticate via Header
    if x_api_key != "secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid API Key"
        )
    
    return {
        "product_name": name,
        "product_price": price,
        "session_active": session_id is not None
    }
```

### 8. API Testing Examples
Submit registration via curl:
```bash
curl -X POST http://127.0.0.1:8000/products \
  -H "x-api-key: secret-token" \
  --cookie "session_id=user1234" \
  -F "name=UltraBook" \
  -F "price=1200.00"
# Response: {"product_name":"UltraBook","product_price":1200.0,"session_active":true}
```

### 9. Common Mistakes
Forgetting that Python parameter names convert hyphens to underscores (e.g., header `X-Custom-Header` matches function parameter `x_custom_header` by default).

### 10. Best Practices
Set `convert_underscores=True` or explicitly define the header name if it deviates from default mappings.

### 11. Interview Questions
* **Q: Why does Python convert dashes to underscores in Header parameter declarations?**
  * *A*: Python variables cannot contain hyphens. FastAPI automatically translates incoming headers like `User-Agent` to `user_agent` to ensure they are valid Python variable names.

### 12. Chapter Summary
FastAPI extracts query fields, headers, cookies, and form variables directly from the request context.

### 13. Practice Exercises
Write an endpoint that inspects a browser cookie and returns a personalized greeting.

---

## Chapter 4: Static Files, File Uploads, & Templates

### 1. Introduction
Web applications often need to serve static assets (CSS, JS, images), process multipart file uploads, and render HTML templates on the server.

### 2. Concept Explanation
* **Why it exists**: Static files enable hosting front-end elements directly. File uploads handle profile pictures or documents, and Jinja2 templates render dynamic server-side pages.
* **When to use it**: Small web portals, email templates, image hosting engines.
* **When NOT to use it**: High-scale cloud storage (use AWS S3) or decoupled Single Page Apps (like React/Vue).
* **Advantages**: Self-contained web stack, easy local development.
* **Disadvantages**: Local file operations are blocking if not managed via async streams, and local disk assets do not scale horizontally.
* **Industry Use Cases**: Admin panels, document upload portals.

### 3. Architecture Explanation
FastAPI mounts a WSGI/ASGI sub-app (`StaticFiles`) for assets and uses `Jinja2Templates` to render HTML templates.
```
FastAPI Router ---> Static Files Directory (/static)
               ---> Jinja2 Engine ---> HTML Template Output
```

### 4. Visual Workflow
```
Client ---> Uploads Resume File ---> FastAPI reads bytes asynchronously ---> Writes to local uploads folder
```

### 5. Real-World Scenario
A job application portal needs to render an upload form, accept resume PDF uploads, and save them in an upload folder.

### 6. Step-by-Step Implementation
1. Create `static/` and `templates/` folders.
2. Install `jinja2` and `python-multipart`.
3. Mount static file routes and configure Jinja templates.

### 7. Source Code Examples
```python
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os

app = FastAPI(title="Upload Portal")

# Setup folder paths
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Write a simple upload form template file inside templates/index.html
# For demo purposes, we will mock HTMLResponse rendering

@app.get("/upload-form", response_class=HTMLResponse)
async def get_upload_form(request: Request):
    # Normally: return templates.TemplateResponse("index.html", {"request": request})
    html_content = """
    <html>
        <body>
            <form action="/upload" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <input type="submit">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/upload")
async def handle_file_upload(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "saved_path": file_path, "content_type": file.content_type}
```

### 8. API Testing Examples
Upload a mock text file:
```bash
echo "Resume details" > my_resume.txt
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@my_resume.txt"
# Response: {"filename":"my_resume.txt","saved_path":"uploads/my_resume.txt","content_type":"text/plain"}
```

### 9. Common Mistakes
Using `file.file.read()` directly without async context on huge files, loading the entire payload into RAM and freezing the application.

### 10. Best Practices
Use `UploadFile` instead of `bytes` because `UploadFile` uses a spool file (stored in memory up to a limit, then written to disk), preventing RAM exhaustion.

### 11. Interview Questions
* **Q: Why should you prefer `UploadFile` over `bytes` for handling file uploads?**
  * *A*: `bytes` forces the entire file to be loaded into memory. `UploadFile` utilizes a temporary spool file, making it highly memory-efficient, and provides access to metadata like filenames and content types.

### 12. Chapter Summary
Multipart forms manage file uploads. `StaticFiles` and templates handle server-rendered content.

### 13. Practice Exercises
Create an endpoint that accepts an image upload, validates that the extension is `.png` or `.jpg`, and returns an error if validation fails.
