from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from test_optimizer import AdvancedTestOptimizer, TestMetrics, OptimizationStrategy

app = FastAPI(title="Test Execution Optimizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def disable_static_cache(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.mount("/static", StaticFiles(directory="static"), name="static")

class TestInfo(BaseModel):
    name: str
    estimated_time: float
    dependencies: List[str]
    priority: int = 1
    resource_usage: Dict[str, float] = {}

class OptimizationRequest(BaseModel):
    tests: List[TestInfo]
    max_parallel: int = 4
    optimization_strategy: str = "time_based"

class OptimizationResult(BaseModel):
    optimized_order: List[str]
    estimated_total_time: float
    parallel_groups: List[List[str]]
    improvement_percentage: float

optimizer = AdvancedTestOptimizer()

@app.post("/optimize", response_model=OptimizationResult)
async def optimize_tests(request: OptimizationRequest):
    try:
        # Convert API models to internal TestMetrics
        test_metrics = [
            TestMetrics(
                name=t.name,
                estimated_time=t.estimated_time,
                dependencies=t.dependencies,
                priority=t.priority,
                resource_usage=t.resource_usage
            ) for t in request.tests
        ]
        
        # Load test suite will validate circular dependencies
        optimizer.load_test_suite(test_metrics)
        
        # Map string strategy to Enum
        try:
            strategy_enum = OptimizationStrategy(request.optimization_strategy)
        except ValueError:
            strategy_enum = OptimizationStrategy.TIME_BASED
            
        # Get optimized results
        result_dict = optimizer.optimize_with_strategy(strategy_enum, request.max_parallel)
        
        # Calculate improvement
        original_time = sum(test.estimated_time for test in request.tests)
        optimized_time = result_dict['estimated_time']
        improvement = ((original_time - optimized_time) / original_time) * 100 if original_time > 0 else 0
        
        return OptimizationResult(
            optimized_order=result_dict['optimized_order'],
            estimated_total_time=optimized_time,
            parallel_groups=result_dict['parallel_groups'],
            improvement_percentage=improvement
        )
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def dashboard():
    return {"message": "Test Execution Optimizer API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
