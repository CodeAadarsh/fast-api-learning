# FastAPI Best Practices

*Understand the architectural patterns, testing strategies, and design principles required to turn a simple script into a scalable, production-ready FastAPI application.*
**Authors:** Raphael do Vale & Juan Cruz Martinez | **Date:** Jan 23, 2026

Python has evolved from a simple language to one of the most used programming languages in the world, dominating fields ranging from data science to high-scale web applications. FastAPI emerged to fill the gap for a framework that combines Python’s simplicity with the performance required for scalable modern systems.

Here are the architectural patterns and best practices required to build production-ready FastAPI applications.

---

## Design REST APIs Using the Correct Verbs and Patterns

### Use the Correct HTTP Verbs

The HTTP protocol defines methods (verbs) that describe the action performed on a given endpoint:

* **GET:** Read data
* **POST:** Create a new resource
* **PUT:** Full update (replace resource)
* **PATCH:** Partial update
* **DELETE:** Remove resource
* **HEAD:** Same as GET, but returns only headers
* **OPTIONS:** Describe available operations or capabilities

**Example (Zoo API):**

* `GET /animals`: Retrieve the list of animals
* `POST /animals`: Create a new animal
* `GET /animals/{id}`: Retrieve a specific animal’s data
* `PUT /animals/{id}`: Replace all data for a specific animal

### Naming Conventions

* Use **plural nouns** for collections (`/animals`, `/users`, `/orders`).
* Use **singular nouns** for individual resources (`/animal`, `/user`, `/order`).
* Keep the resource hierarchy logical (`/animals/1/orders`).
* Use **lowercase** for resource names.

### Versioning

When introducing breaking changes, create a new API version and maintain the old one for a transition period. A common approach is including the version number in the URL (e.g., `/v1/animals`).

---

## Folder Structure

Your folder structure determines how easily your project can grow and how maintainable it will be. A clean, community-recommended structure:

```text
app
├── alembic/            # Database migration files
├── api/                # Routes, HTTP Auth, and HTTP Filters
│   ├── routes/
│   │   ├── animal.py
│   │   └── zookeeper.py
│   └── deps.py
│   └── main.py
├── core/               # System-level code (config, security, db)
│   ├── config.py
│   ├── security.py
│   └── db.py
├── crud.py             # Database operations
├── main.py             # FastAPI startup code
├── models.py           # SQLAlchemy ORM models
├── utils.py
tests/                  # Application tests
├── api/
│   └── test_animals.py
└── utils.py

```

*Note: For very large projects, consider a domain-driven structure where each business domain has its own `router.py`, `schemas.py`, and `models.py`.*

---

## Strong Typing and Data Validation with Pydantic

FastAPI integrates deeply with Pydantic to provide runtime type validation based on Python type hints.

```python
class Species(enum.StrEnum):
   lion = "lion"
   tiger = "tiger"
   elephant = "elephant"

class Animal(BaseModel):
   id: uuid.UUID
   name: str = Field(..., min_length=5)
   date_of_birth: date
   species: Species
   nickname: str | None = None

   @field_validator("date_of_birth")
   @classmethod
   def validate_date_of_birth(cls, v):
       if v > date.today():
           raise ValueError("Date of birth cannot be in the future")
       return v

```

If a user sends invalid data (e.g., an invalid UUID or a name that is too short), FastAPI automatically rejects it with a `400 Bad Request` and structured JSON explaining exactly what failed.

---

## Auto OpenAPI Documentation

When using Pydantic models, FastAPI automatically generates standard OpenAPI documentation, accessible at `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`. You can enhance this UI by adding `examples` directly into your Pydantic `Field` definitions.

---

## Concurrency and Asynchronous Code

FastAPI supports both synchronous and asynchronous code. To make an endpoint async, add the `async` keyword:

```python
@app.get("/animals/{animal_id}")
async def get_animal(animal_id: uuid.UUID):
   ...

```

**Warning:** Async code is for I/O-bound operations (database queries, network requests). Python’s event loop runs on a single thread. Calling a blocking, synchronous library inside an `async` function will block the entire event loop and freeze your application.

---

## Dependency Injection

Dependency Injection (DI) decouples components, making them atomic, replaceable, and independent—highly useful for testability.

Instead of relying on global instances, inject dependencies:

```python
class AnimalDB:
   def __init__(self, pool: AsyncConnectionPool):
       self.pool = pool
       
   def get_animal(self, animal_id: uuid.UUID) -> Animal | None:
       ...

def get_animal_db(pool: AsyncConnectionPool = Depends(get_pool)) -> AnimalDB:
   return AnimalDB(pool)

@app.get("/animals/{animal_id}")
async def get_animal(animal_id: uuid.UUID, animal_db: AnimalDB = Depends(get_animal_db)):
   return await animal_db.get_animal(animal_id)

```

This allows you to easily swap implementations (like mocking a database) during testing without altering production code.

---

## Testing

### Unit Testing

Using Dependency Injection makes unit testing incredibly fast. You can mock external dependencies entirely:

```python
async def test_get_animal():
   mock_animal_db = Mock(spec=AnimalDB)
   expected_animal = Animal(id=uuid.UUID("..."), name="Simba", ...)
   
   mock_animal_db.get_animal.return_value = AsyncMock(return_value=expected_animal)
   returned_animal = await get_animal(expected_animal.id, animal_db=mock_animal_db)
   
   assert returned_animal.id == expected_animal.id

```

### Integration Testing

Use FastAPI's `TestClient` alongside `pytest` for integration testing to verify real HTTP responses:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_animals():
   response = client.get("/animals")
   assert response.status_code == 200
   assert isinstance(response.json(), list)

```

---

## Error Handling

Instead of using `try/except` blocks everywhere, define custom domain exceptions and let FastAPI handle them globally using exception handlers.

**1. Define Domain Exceptions:**

```python
class ZooException(Exception):
   ...  
class AnimalNotFoundError(ZooException):
   ...

```

**2. Create Global Exception Handlers:**

```python
@app.exception_handler(AnimalNotFoundError)
async def animal_not_found_exception_handler(request: Request, exc: AnimalNotFoundError):
   return JSONResponse(
       status_code=404,
       content={"message": "Animal not found"},
   )

```

This keeps your business logic completely decoupled from HTTP protocol specifics. To ensure these custom errors appear in your OpenAPI docs, manually add them to the `responses` dictionary in your route decorators.

---

## Conclusion

Understanding these architectural patterns early will help you make better decisions when your application scales. Avoid over-engineering small APIs, but know when to introduce dependency injection, domain folders, and custom exception handlers to prevent painful refactoring as your system grows.