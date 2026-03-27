# Test Execution Optimizer - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Web Dashboard](#web-dashboard)
4. [REST API](#rest-api)
5. [CLI Usage](#cli-usage)
6. [Configuration](#configuration)
7. [CI/CD Integration](#cicd-integration)
8. [Docker Deployment](#docker-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

Test Execution Optimizer is an intelligent system that reduces test suite runtime by:

- **Optimizing test order** based on dependencies and priorities
- **Enabling parallel execution** with resource constraints
- **Multiple strategies** for different optimization goals

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional)
- Kubernetes (optional)

### Local Installation

```bash
# Clone the repository
git clone <repository-url>
cd test-execution-optimizer

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The API will be available at `http://localhost:8000`

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-01T12:00:00"}
```

---

## Web Dashboard

### Accessing the Dashboard

Open your browser and navigate to:
```
http://localhost:8000/static/dashboard.html
```

### Dashboard Features

1. **Test Suite Input**
   - Add tests with name, estimated time, dependencies, priority
   - Import test suite from JSON
   - Clear/reset test suite

2. **Optimization Settings**
   - Select optimization strategy
   - Configure max parallel tests

3. **Results Display**
   - Optimized execution order
   - Parallel execution groups
   - Estimated total time
   - Improvement percentage

4. **Visualization**
   - Dependency graph view
   - Execution timeline

---

## REST API

### POST /optimize

Optimize test execution order.

**Request:**
```bash
curl -X POST "http://localhost:8000/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "tests": [
      {
        "name": "unit_test_auth",
        "estimated_time": 2.5,
        "dependencies": [],
        "priority": 3,
        "resource_usage": {"cpu": 1, "memory": 512}
      },
      {
        "name": "integration_test_api",
        "estimated_time": 5.0,
        "dependencies": ["unit_test_auth"],
        "priority": 1,
        "resource_usage": {"cpu": 2, "memory": 2048}
      }
    ],
    "max_parallel": 4,
    "optimization_strategy": "time_based"
  }'
```

**Response:**
```json
{
  "optimized_order": ["unit_test_auth", "integration_test_api"],
  "estimated_total_time": 5.0,
  "parallel_groups": [["unit_test_auth"], ["integration_test_api"]],
  "improvement_percentage": 50.0
}
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

### GET /

API information.

```bash
curl http://localhost:8000/
```

---

## CLI Usage

### Example Script

```python
from test_optimizer import AdvancedTestOptimizer, TestMetrics, OptimizationStrategy

# See example_usage.py for comprehensive usage examples

# Create optimizer
optimizer = AdvancedTestOptimizer()

# Define test suite
tests = [
    TestMetrics(
        name="test_auth",
        estimated_time=2.0,
        dependencies=[],
        priority=3,
        resource_usage={"cpu": 1, "memory": 512}
    ),
    TestMetrics(
        name="test_api",
        estimated_time=5.0,
        dependencies=["test_auth"],
        priority=2,
        resource_usage={"cpu": 2, "memory": 2048}
    ),
    TestMetrics(
        name="test_database",
        estimated_time=3.0,
        dependencies=["test_auth"],
        priority=1,
        resource_usage={"cpu": 2, "memory": 1024}
    ),
]

# Load test suite
optimizer.load_test_suite(tests)

# Optimize with strategy
result = optimizer.optimize_with_strategy(
    OptimizationStrategy.TIME_BASED,
    max_parallel=4
)

# Display results
print(f"Optimized Order: {result['optimized_order']}")
print(f"Parallel Groups: {result['parallel_groups']}")
print(f"Estimated Time: {result['estimated_time']}s")
print(f"Improvement: {result.get('improvement_percentage', 0):.1f}%")
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8000 | Server port |
| HOST | 0.0.0.0 | Server host |
| LOG_LEVEL | INFO | Logging level |

### Test Configuration

Each test supports these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | string | required | Unique test identifier |
| estimated_time | float | required | Expected execution time (seconds) |
| dependencies | list | [] | List of test names that must run first |
| priority | int | 1 | Priority level (1-10, higher = more important) |
| resource_usage | dict | {} | CPU and memory requirements |
| failure_rate | float | 0.0 | Historical failure rate (0-1) |

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Optimize Tests
  run: |
    python -c "
    from test_optimizer import AdvancedTestOptimizer
    # Your optimization code here
    "
```

---

## Docker Deployment

### Build Image

```bash
docker build -f infrastructure/docker/Dockerfile -t test-optimizer:latest .
```

### Run Container

```bash
# Basic run
docker run -p 8000:8000 test-optimizer:latest

# With environment variables
docker run -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  -e PORT=8000 \
  test-optimizer:latest

# Using docker-compose
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

### Access Container

```
http://localhost:8000
```



## Optimization Strategies

### Time-Based
- Prioritizes fastest tests first
- Best for quick feedback
- Use case: Development commits

### Priority-Based
- Executes high-priority tests first
- Important for critical path testing
- Use case: Release pipelines

### Resource-Based
- Balances CPU and memory usage
- Optimizes parallel execution
- Use case: Limited resources

---

## Troubleshooting

### Common Issues

#### 1. Circular Dependency Error

**Problem:** `Circular dependencies detected in test suite`

**Solution:** Check your test dependencies and remove cycles:
```python
# Invalid: A -> B -> A
tests = [
    TestMetrics(name="A", dependencies=["B"]),
    TestMetrics(name="B", dependencies=["A"]),
]
```

#### 2. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'networkx'`

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

#### 3. Port Already in Use

**Problem:** `Address already in use`

**Solution:** Change port or stop conflicting service:
```bash
# Check what's using port 8000
lsof -i :8000

# Run on different port
PORT=8080 python main.py
```



---

## API Reference

### Full API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | API information |
| GET | /health | Health check |
| POST | /optimize | Optimize test execution |

### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 500 | Internal Server Error |

---

## Support

For issues and questions:
- Check the README.md
- Review the design document
- Check test files for examples
- Review CI/CD configurations

---

## Quick Reference

```bash
# Start API server
python main.py

# Health check
curl http://localhost:8000/health

# Optimize tests
curl -X POST http://localhost:8000/optimize -H "Content-Type: application/json" -d '{"tests":[{"name":"t1","estimated_time":1},{"name":"t2","estimated_time":2,"dependencies":["t1"]}],"max_parallel":2}'

# Run with Docker
docker run -p 8000:8000 test-optimizer:latest
```