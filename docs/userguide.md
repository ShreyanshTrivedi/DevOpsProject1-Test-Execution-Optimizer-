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
9. [Kubernetes Deployment](#kubernetes-deployment)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

Test Execution Optimizer is an intelligent system that reduces test suite runtime by:

- **Optimizing test order** based on dependencies and priorities
- **Enabling parallel execution** with resource constraints
- **Machine learning predictions** for accurate time estimates
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
    "optimization_strategy": "hybrid"
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
    OptimizationStrategy.HYBRID,
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

### Jenkins

```groovy
pipeline {
    agent any

    stages {
        stage('Optimize Tests') {
            steps {
                script {
                    sh 'python -c "
from test_optimizer import AdvancedTestOptimizer, TestMetrics, OptimizationStrategy
# Your optimization code here
"'
                }
            }
        }
    }
}
```

### GitHub Actions

```yaml
- name: Optimize Tests
  run: |
    python -c "
    from test_optimizer import AdvancedTestOptimizer
    # Your optimization code here
    "
```

### Using CI Integrations Module

```python
from ci_integrations import create_jenkins_integration, create_github_integration

# Jenkins integration
jenkins = create_jenkins_integration(
    jenkins_url="http://jenkins:8080",
    job_name="test-job",
    username="user",
    api_token="your-token"
)

# Get test results from CI
test_results = jenkins.get_test_results()
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

---

## Kubernetes Deployment

### Apply Manifests

```bash
# Using kubectl
kubectl apply -f infrastructure/kubernetes/

# Using kustomize
kubectl apply -k infrastructure/kubernetes/
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -l app=test-optimizer

# Check service
kubectl get svc test-optimizer

# View logs
kubectl logs -l app=test-optimizer
```

### Access Service

```bash
# Port forward for local access
kubectl port-forward svc/test-optimizer 8000:80

# Or use ingress (if configured)
http://test-optimizer.local
```

### Scaling

```bash
# Manual scale
kubectl scale deployment test-optimizer --replicas=5

# Auto-scaling is configured via HPA
# Scales between 2-10 replicas based on CPU/memory
```

---

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

### ML-Based
- Uses machine learning predictions
- Learns from historical data
- Best accuracy over time

### Hybrid
- Combines time, priority, and failure rate
- Best overall performance
- Recommended for most use cases

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

#### 4. Kubernetes Pod Crash

**Problem:** Pods in CrashLoopBackOff

**Solution:** Check logs:
```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

#### 5. ML Model Not Training

**Problem:** `is_trained` remains False

**Solution:** Record more execution results:
```python
# Record at least 5 execution results
for i in range(10):
    optimizer.record_execution_result("test1", 2.5, True)
```

---

## API Reference

### Full API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | API information |
| GET | /health | Health check |
| POST | /optimize | Optimize test execution |
| GET | /metrics | Performance metrics |
| POST | /history/record | Record execution result |

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

# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/
```