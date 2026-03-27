# API Documentation

## Test Execution Optimizer API

Base URL: `http://localhost:8000`

---

## Endpoints

### GET /

Returns API information.

**Response:**
```json
{
  "message": "Test Execution Optimizer API",
  "version": "1.0.0"
}
```

---

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### POST /optimize

Optimizes test execution order based on provided test suite.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| tests | array | Yes | List of test objects |
| max_parallel | integer | No | Maximum parallel tests (default: 4) |
| optimization_strategy | string | No | Strategy name (default: time_based) |

**Test Object:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Unique test identifier |
| estimated_time | float | Yes | Expected execution time (seconds) |
| dependencies | array | No | List of test names that must run first |
| priority | integer | No | Priority level 1-10 (default: 1) |
| resource_usage | object | No | CPU and memory requirements |

**Resource Usage Object:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| cpu | float | 1 | CPU units required |
| memory | float | 512 | Memory in MB |

**Example Request:**
```json
{
  "tests": [
    {
      "name": "unit_test_auth",
      "estimated_time": 2.5,
      "dependencies": [],
      "priority": 3,
      "resource_usage": {
        "cpu": 1,
        "memory": 512
      }
    },
    {
      "name": "integration_test_api",
      "estimated_time": 5.0,
      "dependencies": ["unit_test_auth"],
      "priority": 1,
      "resource_usage": {
        "cpu": 2,
        "memory": 2048
      }
    },
    {
      "name": "test_database",
      "estimated_time": 3.0,
      "dependencies": ["unit_test_auth"],
      "priority": 2,
      "resource_usage": {
        "cpu": 2,
        "memory": 1024
      }
    }
  ],
  "max_parallel": 4,
  "optimization_strategy": "time_based"
}
```

**Success Response (200):**
```json
{
  "optimized_order": [
    "unit_test_auth",
    "integration_test_api",
    "test_database"
  ],
  "estimated_total_time": 5.0,
  "parallel_groups": [
    ["unit_test_auth"],
    ["integration_test_api", "test_database"]
  ],
  "improvement_percentage": 50.0
}
```

**Error Response (400):**
```json
{
  "detail": "Circular dependencies detected in test suite"
}
```

**Error Response (500):**
```json
{
  "detail": "Internal server error message"
}
```

---

## Data Models

### TestInfo

```python
class TestInfo(BaseModel):
    name: str                           # Unique test identifier
    estimated_time: float               # Expected execution time in seconds
    dependencies: List[str] = []        # List of dependency test names
    priority: int = 1                   # Priority 1-10 (higher = more important)
    resource_usage: Dict[str, float] = {}  # CPU and memory requirements
```

### OptimizationRequest

```python
class OptimizationRequest(BaseModel):
    tests: List[TestInfo]              # List of tests to optimize
    max_parallel: int = 4               # Maximum parallel tests
    optimization_strategy: str = "time_based"  # Optimization strategy
```

### OptimizationResult

```python
class OptimizationResult(BaseModel):
    optimized_order: List[str]         # Optimized test execution order
    estimated_total_time: float         # Estimated total execution time
    parallel_groups: List[List[str]]    # Groups of tests that can run in parallel
    improvement_percentage: float       # Improvement over sequential execution
```

---

## Optimization Strategies

### time_based

Prioritizes faster tests first for quick feedback.

**Best for:** Development commits, quick validation

### priority_based

Executes high-priority tests first.

**Best for:** Critical path testing, release pipelines

### resource_based

Balances CPU and memory usage for optimal parallel execution.

**Best for:** Resource-constrained environments

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Invalid request body or circular dependencies |
| 500 | Internal Error | Server error |

---

## Rate Limiting

Currently no rate limiting is enforced. For production deployments, consider adding rate limiting middleware.

---

## Authentication

Currently the API is open (no authentication). For production:

1. Add JWT authentication
2. Use API keys
3. Implement OAuth2

---

## Examples

### Python Client

```python
import requests

url = "http://localhost:8000/optimize"

payload = {
    "tests": [
        {
            "name": "test_auth",
            "estimated_time": 2.0,
            "dependencies": [],
            "priority": 3
        },
        {
            "name": "test_api",
            "estimated_time": 5.0,
            "dependencies": ["test_auth"],
            "priority": 2
        }
    ],
    "max_parallel": 4,
    "optimization_strategy": "time_based"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Optimized Order: {result['optimized_order']}")
print(f"Estimated Time: {result['estimated_total_time']}s")
print(f"Improvement: {result['improvement_percentage']}%")
```

### cURL

```bash
curl -X POST "http://localhost:8000/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "tests": [
      {"name": "t1", "estimated_time": 2.0},
      {"name": "t2", "estimated_time": 3.0, "dependencies": ["t1"]}
    ],
    "max_parallel": 4,
    "optimization_strategy": "time_based"
  }'
```

### JavaScript (Node.js)

```javascript
const response = await fetch('http://localhost:8000/optimize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    tests: [
      { name: 'test_auth', estimated_time: 2.0, dependencies: [] },
      { name: 'test_api', estimated_time: 5.0, dependencies: ['test_auth'] }
    ],
    max_parallel: 4,
    optimization_strategy: 'time_based'
  })
});

const result = await response.json();
console.log(result);
```

---

## Swagger UI

Interactive API documentation is available at:

```
http://localhost:8000/docs
```

This provides:
- Interactive API testing
- Request/response schema exploration
- Code generation for various languages

---

## OpenAPI Schema

The full OpenAPI 3.0 schema is available at:

```
http://localhost:8000/openapi.json
```

---

## Versioning

Current API Version: **1.0.0**

Future versions will be available at:
- `/v1/optimize`
- `/v2/optimize`

---

## Changelog

### v1.0.0 (Current)
- Initial release
- POST /optimize endpoint
- GET /health endpoint
- Multiple optimization strategies
- Parallel execution groups