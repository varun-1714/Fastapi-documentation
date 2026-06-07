# Part 12: GraphQL

---

## Chapter 1: Strawberry GraphQL Integration (Product Catalog API)

### 1. Introduction
GraphQL is a query language for APIs that allows clients to request the exact data they need, making it an efficient alternative to REST. Strawberry is a modern, developer-friendly Python library for building GraphQL APIs using Python type hints.

### 2. Concept Explanation
* **Why it exists**: REST APIs often return too much data (over-fetching) or require multiple requests to different routes to gather related data (under-fetching). GraphQL solves this by exposing a single endpoint where clients request specific fields.
* **When to use it**: Client applications with varying data requirements (e.g. dashboards, mobile apps), aggregations of multiple services, APIs with highly relational data models.
* **When NOT to use it**: Simple CRUD applications, binary file transfer portals, or when REST's simple caching model (by URI) is preferred.
* **Advantages**: No over-fetching or under-fetching, strongly typed schemas, single endpoint for all operations, built-in documentation and playgrounds.
* **Disadvantages**: Complex queries can overload the database (requires N+1 query optimization), caching is more complex because requests are sent via POST.
* **Industry Use Cases**: GitHub, Shopify, and Facebook use GraphQL for client-facing APIs.

### 3. Architecture Explanation
Strawberry compiles Python classes into a GraphQL schema. FastAPI mounts a dedicated sub-app to serve the GraphQL endpoint and the GraphiQL playground.
```
Client Request (POST) ---> FastAPI Mount ---> Strawberry Resolver ---> DB Query ---> JSON Response
```

### 4. Visual Workflow
```
Client Query: { product { name } } ---> Resolver executes ---> Database fetches name ---> Response JSON
```

### 5. Real-World Scenario
An e-commerce product catalog needs to support multiple client layouts, allowing them to request different combinations of product names, prices, and inventory levels.

### 6. Step-by-Step Implementation
1. Install Strawberry and FastAPI: `pip install strawberry-graphql fastapi`.
2. Define GraphQL types using Strawberry decorators.
3. Implement query and mutation resolvers.
4. Mount the Strawberry router inside the FastAPI application.

### 7. Source Code Examples
```python
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# 1. Define GraphQL Types
@strawberry.type
class Product:
    id: int
    name: str
    price: float
    category: str

# Mock Database
PRODUCTS_DB = [
    Product(id=1, name="Laptop", price=999.99, category="Electronics"),
    Product(id=2, name="Coffee Mug", price=14.99, category="Kitchen"),
]

# 2. Define Query Resolvers
@strawberry.type
class Query:
    @strawberry.field
    def get_products(self, category: str | None = None) -> list[Product]:
        if category:
            return [p for p in PRODUCTS_DB if p.category == category]
        return PRODUCTS_DB

    @strawberry.field
    def get_product(self, id: int) -> Product | None:
        for p in PRODUCTS_DB:
            if p.id == id:
                return p
        return None

# 3. Define Mutation Resolvers
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(self, name: str, price: float, category: str) -> Product:
        new_id = len(PRODUCTS_DB) + 1
        product = Product(id=new_id, name=name, price=price, category=category)
        PRODUCTS_DB.append(product)
        return product

# 4. Compile Schema and Integrate Router
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="GraphQL Product API")
app.include_router(graphql_app, prefix="/graphql")
```

### 8. API Testing Examples
Run the server:
```bash
uvicorn main:app --reload
```
Open `http://localhost:8000/graphql` to access the GraphiQL dashboard. Submit this query to fetch products:
```graphql
query {
  getProducts(category: "Electronics") {
    name
    price
  }
}
# Response:
# {
#   "data": {
#     "getProducts": [
#       {
#         "name": "Laptop",
#         "price": 999.99
#       }
#     ]
#   }
# }
```

### 9. Common Mistakes
Writing resolver operations that trigger N+1 queries when fetching nested child tables.

### 10. Best Practices
Use tools like dataloader (e.g. `strawberry.dataloader.DataLoader`) to batch and cache database queries, avoiding performance degradation from nested queries.

### 11. Interview Questions
* **Q: What is the N+1 problem in GraphQL and how do you solve it?**
  * *A*: The N+1 problem occurs when a resolver queries the database for a parent record, and then queries the database again for each child record individually. It is solved using dataloaders, which batch and cache database requests to fetch all children in a single query.

### 12. Chapter Summary
Strawberry integrates with FastAPI using decorators and type hints. Queries read data, and mutations write or update it.

### 13. Practice Exercises
Add a mutation `deleteProduct(id: Int!)` that removes a product from the database by its ID.
