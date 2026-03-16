"""
Enhanced API endpoints for Test Execution Optimizer
Integrates advanced optimization algorithms with CI/CD integrations
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from test_optimizer import AdvancedTestOptimizer, TestMetrics, OptimizationStrategy
from ci_integrations import CIIntegrationManager, create_jenkins_integration, create_github_integration, create_gitlab_integration
import json
import asyncio
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test Execution Optimizer API",
    description="Advanced test execution optimization with ML and CI/CD integrations",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global optimizer instance
optimizer = AdvancedTestOptimizer()
ci_manager = CIIntegrationManager()

# Pydantic models
class TestInfo(BaseModel):
    name: str = Field(..., description="Test name/identifier")
    estimated_time: float = Field(..., gt=0, description="Estimated execution time in seconds")
    dependencies: List[str] = Field(default_factory=list, description="List of test dependencies")
    priority: int = Field(default=1, ge=1, le=10, description="Test priority (1-10)")
    resource_usage: Dict[str, float] = Field(default_factory=dict, description="Resource requirements")
    failure_rate: float = Field(default=0.0, ge=0, le=1, description="Historical failure rate")

class OptimizationRequest(BaseModel):
    tests: List[TestInfo]
    max_parallel: int = Field(default=4, ge=1, le=20, description="Maximum parallel tests")
    optimization_strategy: str = Field(default="hybrid", description="Optimization strategy")
    enable_ml: bool = Field(default=True, description="Enable ML predictions")
    
class OptimizationResult(BaseModel):
    optimized_order: List[str]
    estimated_total_time: float
    parallel_groups: List[List[str]]
    improvement_percentage: float
    strategy_used: str
    optimization_id: str
    metadata: Dict[str, Any]

class CIIntegrationRequest(BaseModel):
    platform: str = Field(..., description="CI platform (jenkins, github, gitlab)")
    config: Dict[str, Any] = Field(..., description="Platform-specific configuration")
    
class ExecutionResult(BaseModel):
    test_name: str
    actual_time: float
    success: bool
    timestamp: datetime

class OptimizationReport(BaseModel):
    test_count: int
    original_time: float
    strategy_comparison: Dict[str, Dict[str, float]]
    historical_executions: int
    ml_trained: bool
    recommendations: List[str]

# Dependency functions
def get_optimizer():
    return optimizer

def get_ci_manager():
    return ci_manager

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Test Execution Optimizer API v2.0",
        "features": [
            "Advanced optimization algorithms",
            "Machine learning predictions",
            "CI/CD integrations",
            "Real-time dashboard"
        ],
        "endpoints": {
            "optimize": "/optimize",
            "ci_integrate": "/ci/integrate",
            "report": "/report",
            "health": "/health"
        }
    }

@app.post("/optimize", response_model=OptimizationResult)
async def optimize_tests(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    opt: AdvancedTestOptimizer = Depends(get_optimizer)
):
    """
    Optimize test execution order using advanced algorithms
    """
    try:
        # Generate optimization ID
        optimization_id = str(uuid.uuid4())
        
        # Convert TestInfo to TestMetrics
        test_metrics = []
        for test in request.tests:
            test_metric = TestMetrics(
                name=test.name,
                estimated_time=test.estimated_time,
                dependencies=test.dependencies,
                priority=test.priority,
                resource_usage=test.resource_usage,
                failure_rate=test.failure_rate
            )
            test_metrics.append(test_metric)
        
        # Load test suite
        opt.load_test_suite(test_metrics)
        
        # Train ML models if enabled and sufficient data
        if request.enable_ml and len(opt.execution_history) >= 5:
            background_tasks.add_task(opt.train_ml_models)
        
        # Get optimization strategy
        try:
            strategy = OptimizationStrategy(request.optimization_strategy)
        except ValueError:
            strategy = OptimizationStrategy.HYBRID
        
        # Perform optimization
        result = opt.optimize_with_strategy(strategy, request.max_parallel)
        
        # Calculate improvement
        original_time = sum(test.estimated_time for test in request.tests)
        improvement = ((original_time - result['estimated_time']) / original_time) * 100 if original_time > 0 else 0
        
        # Generate metadata
        metadata = {
            "test_count": len(request.tests),
            "dependency_levels": len(set(
                len(list(opt.dependency_graph.predecessors(test))) 
                for test in opt.dependency_graph.nodes()
            )),
            "parallel_efficiency": len(result['parallel_groups']) / len(request.tests),
            "ml_enabled": request.enable_ml,
            "optimization_timestamp": datetime.now().isoformat()
        }
        
        return OptimizationResult(
            optimized_order=result['optimized_order'],
            estimated_total_time=result['estimated_time'],
            parallel_groups=result['parallel_groups'],
            improvement_percentage=improvement,
            strategy_used=result['strategy'],
            optimization_id=optimization_id,
            metadata=metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail="Internal optimization error")

@app.post("/ci/integrate")
async def integrate_ci_platform(
    request: CIIntegrationRequest,
    manager: CIIntegrationManager = Depends(get_ci_manager)
):
    """
    Integrate with CI/CD platform
    """
    try:
        if request.platform.lower() == "jenkins":
            integration = create_jenkins_integration(
                jenkins_url=request.config.get("jenkins_url"),
                job_name=request.config.get("job_name"),
                username=request.config.get("username"),
                password=request.config.get("password")
            )
        elif request.platform.lower() == "github":
            integration = create_github_integration(
                repo_owner=request.config.get("repo_owner"),
                repo_name=request.config.get("repo_name"),
                token=request.config.get("token")
            )
        elif request.platform.lower() == "gitlab":
            integration = create_gitlab_integration(
                project_id=request.config.get("project_id"),
                token=request.config.get("token"),
                gitlab_url=request.config.get("gitlab_url", "https://gitlab.com")
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")
        
        # Register integration
        manager.register_integration(request.platform, integration)
        
        # Get test suite from CI
        test_suite = integration.get_test_suite()
        
        return {
            "platform": request.platform,
            "status": "integrated",
            "test_count": len(test_suite),
            "test_suite": test_suite
        }
        
    except Exception as e:
        logger.error(f"CI integration error: {e}")
        raise HTTPException(status_code=500, detail=f"CI integration failed: {str(e)}")

@app.post("/execution/result")
async def record_execution_result(
    result: ExecutionResult,
    opt: AdvancedTestOptimizer = Depends(get_optimizer)
):
    """
    Record test execution result for ML learning
    """
    try:
        opt.record_execution_result(
            test_name=result.test_name,
            actual_time=result.actual_time,
            success=result.success
        )
        
        return {
            "status": "recorded",
            "test_name": result.test_name,
            "timestamp": result.timestamp,
            "total_executions": len(opt.execution_history)
        }
        
    except Exception as e:
        logger.error(f"Result recording error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record execution result")

@app.get("/report", response_model=OptimizationReport)
async def get_optimization_report(
    opt: AdvancedTestOptimizer = Depends(get_optimizer)
):
    """
    Get comprehensive optimization report
    """
    try:
        report = opt.get_optimization_report()
        
        # Generate recommendations
        recommendations = []
        if report.get("ml_trained", False):
            recommendations.append("ML models are trained and providing accurate predictions")
        else:
            recommendations.append("Run more tests to enable ML-based optimizations")
        
        if report.get("historical_executions", 0) < 20:
            recommendations.append("Gather more execution data for better optimizations")
        
        best_strategy = max(report.get("strategy_comparison", {}).items(), 
                          key=lambda x: x[1].get("improvement_percentage", 0), 
                          default=(None, {}))
        if best_strategy[0]:
            recommendations.append(f"Best performing strategy: {best_strategy[0]}")
        
        return OptimizationReport(
            test_count=report.get("test_count", 0),
            original_time=report.get("original_time", 0),
            strategy_comparison=report.get("strategy_comparison", {}),
            historical_executions=report.get("historical_executions", 0),
            ml_trained=report.get("ml_trained", False),
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@app.get("/ci/platforms")
async def list_ci_platforms(
    manager: CIIntegrationManager = Depends(get_ci_manager)
):
    """
    List available CI platforms and integrations
    """
    try:
        return {
            "registered_integrations": manager.list_integrations(),
            "auto_detected": manager.auto_detect_ci(),
            "supported_platforms": ["jenkins", "github", "gitlab", "azure_devops"]
        }
        
    except Exception as e:
        logger.error(f"CI platforms error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list CI platforms")

@app.get("/health")
async def health_check():
    """
    Comprehensive health check
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "components": {
                "optimizer": "operational",
                "ci_integrations": "operational",
                "ml_models": "trained" if optimizer.ml_optimizer.is_trained else "training"
            },
            "metrics": {
                "total_optimizations": len(optimizer.optimization_cache),
                "historical_executions": len(optimizer.execution_history),
                "registered_ci_integrations": len(ci_manager.integrations)
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/strategies")
async def list_optimization_strategies():
    """
    List available optimization strategies
    """
    return {
        "strategies": [
            {
                "name": "time_based",
                "description": "Prioritizes faster tests for quick feedback",
                "best_for": "Small test suites, quick iterations"
            },
            {
                "name": "priority_based",
                "description": "Executes high-priority tests first",
                "best_for": "Critical test coverage, smoke tests"
            },
            {
                "name": "resource_based",
                "description": "Balances CPU and memory usage",
                "best_for": "Resource-constrained environments"
            },
            {
                "name": "ml_based",
                "description": "Uses machine learning for predictions",
                "best_for": "Mature test suites with historical data"
            },
            {
                "name": "hybrid",
                "description": "Combines multiple optimization factors",
                "best_for": "Most scenarios, balanced approach"
            }
        ]
    }

# Background task for periodic ML training
async def periodic_ml_training():
    """Background task to periodically train ML models"""
    while True:
        await asyncio.sleep(3600)  # Train every hour
        try:
            if len(optimizer.execution_history) >= 5:
                optimizer.train_ml_models()
                logger.info("Periodic ML training completed")
        except Exception as e:
            logger.error(f"Periodic ML training failed: {e}")

# Start background task
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    asyncio.create_task(periodic_ml_training())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
