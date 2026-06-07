# Part 4: Pydantic V2

---

## Chapter 1: BaseModel & Validation Mechanics

### 1. Introduction
Pydantic is Python's leading data validation and parsing library. Pydantic V2 is rewritten in Rust, providing a massive speed boost and a cleaner API than its predecessor.

### 2. Concept Explanation
* **Why it exists**: Python lacks strict runtime type enforcement. Pydantic guarantees that incoming data conforms to defined schemas, coercing values where possible.
* **When to use it**: Validation of HTTP request bodies, configuration parsing, database serialization schemas.
* **When NOT to use it**: For low-overhead mathematical operations or when performance requirements make execution speed critical (though V2's Rust core makes it fast enough for almost all use cases).
* **Advantages**: High performance, strict and lax validation modes, type safety, integration with OpenAPI.
* **Disadvantages**: Minor startup overhead when compiling schemas at import time.
* **Industry Use Cases**: Request/Response data parsing, config validation.

### 3. Architecture Explanation
Pydantic compiles Python type annotations into a Rust validation tree. When parsing data, it goes through this validation engine and outputs verified models or raises detailed validation errors.
```
Raw JSON ---> [ Rust Validation Core ] ---> Python BaseModel Instance (Success)
                                       ---> ValidationError (Failure)
```

### 4. Visual Workflow
```
Input Payload: {"price": "19.99"} ---> Core Validator ---> Coerces to float: 19.99 ---> Model populated
```

### 5. Real-World Scenario
A transaction API needs to ingest transaction records, ensuring that ID formats, price currencies, and dates conform to ISO standards.

### 6. Step-by-Step Implementation
1. Install `pydantic`.
2. Declare schemas using `BaseModel`.

### 7. Source Code Examples
```python
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime

class Transaction(BaseModel):
    transaction_id: int
    amount: float = Field(..., gt=0.0)
    currency: str = Field(..., min_length=3, max_length=3)
    created_at: datetime

if __name__ == "__main__":
    # Test valid input
    try:
        t = Transaction(
            transaction_id=101, 
            amount="45.50",  # String gets coerced to float
            currency="USD", 
            created_at="2026-06-07T12:00:00"
        )
        print("Success:", t)
        print("Serialized:", t.model_dump())
    except ValidationError as e:
        print("Validation Failed:", e.json())
```

### 8. API Testing Examples
Verify parsing errors in terminal:
```bash
python pydantic_demo.py
# Output:
# Success: transaction_id=101 amount=45.5 currency='USD' created_at=datetime.datetime(...)
# Serialized: {'transaction_id': 101, 'amount': 45.5, 'currency': 'USD', 'created_at': datetime.datetime(...)}
```

### 9. Common Mistakes
Using standard Python constructors (like `__init__` override) incorrectly, bypassing Pydantic's internal validation tree.

### 10. Best Practices
Use `Field()` to attach validation criteria and metadata. Leverage `model_dump(exclude_unset=True)` to serialize only updated data.

### 11. Interview Questions
* **Q: What is the difference between `model_dump()` and `dict()` in Pydantic?**
  * *A*: `dict()` was the Pydantic V1 API. In Pydantic V2, `dict()` is deprecated and replaced by `model_dump()`. The V2 method performs faster, direct serialization using the underlying Rust engine.

### 12. Chapter Summary
Pydantic V2 uses a Rust engine to validate data, making it much faster. Its declarative models simplify data validation.

### 13. Practice Exercises
Create a BaseModel for a user registration schema validating that name contains only letters.

---

## Chapter 2: Custom Validators & Computed Fields

### 1. Introduction
While built-in constraints cover basic validation needs, enterprise systems often require custom validation logic and fields computed dynamically from existing data.

### 2. Concept Explanation
* **Why it exists**: Pydantic's basic validators cannot check complex domain rules, such as matching passwords or calculating an employee's age dynamically based on their date of birth.
* **When to use it**: Validation of password security, relative date orders, status transitions.
* **When NOT to use it**: Simple validation that can be handled using built-in constraint properties in `Field`.
* **Advantages**: Clean encapsulation of validation logic, declarative computed attributes.
* **Disadvantages**: Overuse of validators can slow down serialization.
* **Industry Use Cases**: Security credentials checking, dynamic pricing computations.

### 3. Architecture Explanation
Pydantic executes validators in two phases: `@field_validator` validates individual fields, and `@model_validator` executes multi-field validations across the entire model structure.
```
Validate Fields (field_validator) ---> Validate Model (model_validator) ---> Computed Fields (@computed_field)
```

### 4. Visual Workflow
```
[Raw Password] ---> field_validator(check length/symbols) ---> passes ---> hash created
```

### 5. Real-World Scenario
A signup schema needs to ensure the `password` and `confirm_password` fields match, and compute the user's `initials` from their full name.

### 6. Step-by-Step Implementation
1. Import `field_validator`, `model_validator`, and `computed_field`.
2. Construct the validation logic inside the model.

### 7. Source Code Examples
```python
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field

class SignupRequest(BaseModel):
    full_name: str
    password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator('full_name')
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        if ' ' not in v.strip():
            raise ValueError('Full name must include both first and last name')
        return v.title()

    @model_validator(mode='after')
    def passwords_match(self) -> 'SignupRequest':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

    @computed_field
    @property
    def initials(self) -> str:
        parts = self.full_name.split()
        return "".join([p[0].upper() for p in parts if p])
```

### 8. API Testing Examples
Testing validations programmatically:
```python
# Should fail because passwords do not match
try:
    SignupRequest(full_name="John Doe", password="securepass1", confirm_password="differentpass")
except ValueError as e:
    print(e)
```

### 9. Common Mistakes
Forgetting that `@field_validator` must be a `@classmethod`.

### 10. Best Practices
Set `mode='after'` in model validators to ensure individual fields are validated before the model-level validator runs.

### 11. Interview Questions
* **Q: How does `mode='before'` differ from `mode='after'` in field validation?**
  * *A*: `mode='before'` runs validation on raw input before Pydantic coerces it (e.g. validating a raw string before parsing to datetime). `mode='after'` runs on coerced Python types.

### 12. Chapter Summary
Custom validators enforce complex logic across fields, and computed fields append read-only data attributes to your responses.

### 13. Practice Exercises
Add a validator to an Invoice schema that ensures the invoice date is in the future.

---

## Chapter 3: Advanced Pydantic: Generics & Settings

### 1. Introduction
Large APIs benefit from generic response containers, while configuration files need to be parsed from environment variables securely.

### 2. Concept Explanation
* **Why it exists**: Setting up standardized JSON envelopes (e.g., matching a uniform response format with varying nested data payloads) is simplified with generics. Settings management reads variables from `.env` files automatically.
* **When to use it**: Standardized API responses, database paging envelopes, environmental configuration parsing.
* **When NOT to use it**: Minimal microservices where config variables are hard-coded or environment variables are not used.
* **Advantages**: Clean code reuse, type safety across responses.
* **Disadvantages**: Requires installing `pydantic-settings` as a separate dependency in Pydantic V2.
* **Industry Use Cases**: Unified JSON response schemas, config validation.

### 3. Architecture Explanation
Generic models map generic placeholder types to specific classes at runtime. Settings models load environmental values and coerce types during initialization.
```
API Response ---> Generic Envelope [T] ---> Payload Schema (User, Order, etc.)
```

### 4. Visual Workflow
```
[ .env File ] ---> BaseSettings ---> Read variables ---> Coerce to typed config object
```

### 5. Real-World Scenario
An API needs to return all query listings inside a uniform data wrapper containing pagination details.

### 6. Step-by-Step Implementation
1. Install `pydantic-settings`.
2. Construct generic models and a mock settings manager.

### 7. Source Code Examples
```python
from typing import Generic, TypeVar
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# Generic Parameter
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    status: str
    code: int
    data: T

class UserProfile(BaseModel):
    username: str
    email: str

# Config Settings
class AppConfig(BaseSettings):
    db_port: int = 5432
    debug_mode: bool = False

    class Config:
        env_prefix = "APP_"

if __name__ == "__main__":
    # Test Generic Response
    response = APIResponse[UserProfile](
        status="success",
        code=200,
        data=UserProfile(username="alice", email="alice@corp.com")
    )
    print(response.model_dump())
```

### 8. API Testing Examples
Verify settings validation works when loading mock variables:
```bash
python generic_settings.py
# Output: {'status': 'success', 'code': 200, 'data': {'username': 'alice', 'email': 'alice@corp.com'}}
```

### 9. Common Mistakes
Forgetting that environment variables are loaded as strings, and failing to define default type annotations for settings fields.

### 10. Best Practices
Set default fallback values inside configurations to avoid application boot crashes if environment keys are missing.

### 11. Interview Questions
* **Q: How does Pydantic Settings handle type casting of environmental variables?**
  * *A*: Pydantic Settings parses environment strings based on the type annotations defined in the `BaseSettings` class (e.g. parsing `"True"` into `True` or `"3306"` into `3306`).

### 12. Chapter Summary
Generics ensure consistent response formats. Settings structures load config values safely.

### 13. Practice Exercises
Define a generic pagination container that accepts items of type `T` and tracks current page offset properties.

---

## Chapter 4: Pydantic V1 to V2 Migration Guide

### 1. Introduction
Upgrading APIs to Pydantic V2 improves validation performance but requires updating deprecated methods.

### 2. Concept Explanation
Pydantic V2 introduces breaking namespace changes, renaming key validation methods and moving components like settings to separate packages.

### 3. Key Renames and Changes

| Pydantic V1 | Pydantic V2 |
| :--- | :--- |
| `dict()` | `model_dump()` |
| `parse_obj()` | `model_validate()` |
| `json()` | `model_dump_json()` |
| `schema()` | `model_json_schema()` |
| `class Config:` | `model_config = SettingsDict(...)` |
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |

### 4. Migration Example (Before and After)

#### V1 Syntax (Deprecated)
```python
# Pydantic V1
from pydantic import BaseModel, validator

class OldUser(BaseModel):
    name: str
    age: int

    @validator('age')
    def val_age(cls, v):
        if v < 18:
            raise ValueError('Underage')
        return v

    class Config:
        orm_mode = True
```

#### V2 Syntax (Modern)
```python
# Pydantic V2
from pydantic import BaseModel, field_validator

class NewUser(BaseModel):
    name: str
    age: int

    @field_validator('age')
    @classmethod
    def val_age(cls, v: int) -> int:
        if v < 18:
            raise ValueError('Underage')
        return v

    model_config = {"from_attributes": True}
```

### 5. Step-by-Step Migration Process
1. Run `bump-pydantic` CLI command on the target repository to automate code replacement.
2. Replace `orm_mode = True` with `from_attributes = True`.
3. Install `pydantic-settings` if utilizing `BaseSettings`.
4. Update custom validators to use the `@field_validator` and `@model_validator` decorators.
5. Run the test suite to verify validation errors are caught correctly.
