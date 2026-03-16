from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import networkx as nx
import numpy as np
from sklearn.linear_model import LinearRegression
import json
import asyncio
from datetime import datetime

app = FastAPI(title="Test Execution Optimizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

class TestOptimizer:
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.execution_history = []
        
    def build_dependency_graph(self, tests: List[TestInfo]):
        self.dependency_graph.clear()
        for test in tests:
            self.dependency_graph.add_node(test.name, 
                                         time=test.estimated_time,
                                         priority=test.priority,
                                         resources=test.resource_usage)
            for dep in test.dependencies:
                self.dependency_graph.add_edge(dep, test.name)
    
    def topological_sort_with_priority(self) -> List[str]:
        try:
            # Get topological order
            topo_order = list(nx.topological_sort(self.dependency_graph))
            
            # Sort by priority within each level
            levels = {}
            for node in topo_order:
                level = nx.shortest_path_length(self.dependency_graph, 
                                               source=list(self.dependency_graph.nodes())[0], 
                                               target=node) if list(self.dependency_graph.nodes()) else 0
                if level not in levels:
                    levels[level] = []
                levels[level].append(node)
            
            for level in levels:
                levels[level].sort(key=lambda x: self.dependency_graph.nodes[x]['priority'], 
                                 reverse=True)
            
            optimized_order = []
            for level in sorted(levels.keys()):
                optimized_order.extend(levels[level])
            
            return optimized_order
        except nx.NetworkXError:
            return list(self.dependency_graph.nodes())
    
    def optimize_parallel_execution(self, max_parallel: int) -> List[List[str]]:
        optimized_order = self.topological_sort_with_priority()
        parallel_groups = []
        
        remaining_tests = optimized_order.copy()
        
        while remaining_tests:
            current_group = []
            current_resources = {"cpu": 0, "memory": 0}
            
            for test in remaining_tests[:]:
                test_resources = self.dependency_graph.nodes[test].get('resources', {})
                test_cpu = test_resources.get('cpu', 1)
                test_memory = test_resources.get('memory', 1)
                
                # Check if test can run in parallel (no dependencies in current group)
                can_run_parallel = True
                for running_test in current_group:
                    if (self.dependency_graph.has_edge(test, running_test) or 
                        self.dependency_graph.has_edge(running_test, test)):
                        can_run_parallel = False
                        break
                
                # Check resource constraints
                if (can_run_parallel and 
                    len(current_group) < max_parallel and
                    current_resources["cpu"] + test_cpu <= max_parallel and
                    current_resources["memory"] + test_memory <= max_parallel * 2):
                    
                    current_group.append(test)
                    current_resources["cpu"] += test_cpu
                    current_resources["memory"] += test_memory
                    remaining_tests.remove(test)
            
            if current_group:
                parallel_groups.append(current_group)
            else:
                # If no tests can be added, take the first one
                parallel_groups.append([remaining_tests.pop(0)])
        
        return parallel_groups
    
    def calculate_total_time(self, parallel_groups: List[List[str]]) -> float:
        total_time = 0
        for group in parallel_groups:
            group_time = max(self.dependency_graph.nodes[test].get('time', 1) 
                           for test in group) if group else 0
            total_time += group_time
        return total_time
    
    def predict_execution_time(self, test_name: str) -> float:
        if not self.execution_history:
            return 1.0
        
        # Simple linear regression based on history
        times = [record['time'] for record in self.execution_history 
                if record['test'] == test_name]
        
        if times:
            return np.mean(times)
        
        # Use average of all tests as fallback
        all_times = [record['time'] for record in self.execution_history]
        return np.mean(all_times) if all_times else 1.0

optimizer = TestOptimizer()

@app.post("/optimize", response_model=OptimizationResult)
async def optimize_tests(request: OptimizationRequest):
    try:
        # Build dependency graph
        optimizer.build_dependency_graph(request.tests)
        
        # Check for circular dependencies
        if not nx.is_directed_acyclic_graph(optimizer.dependency_graph):
            raise HTTPException(status_code=400, detail="Circular dependencies detected")
        
        # Get optimized order
        optimized_order = optimizer.topological_sort_with_priority()
        
        # Create parallel groups
        parallel_groups = optimizer.optimize_parallel_execution(request.max_parallel)
        
        # Calculate times
        original_time = sum(test.estimated_time for test in request.tests)
        optimized_time = optimizer.calculate_total_time(parallel_groups)
        improvement = ((original_time - optimized_time) / original_time) * 100 if original_time > 0 else 0
        
        return OptimizationResult(
            optimized_order=optimized_order,
            estimated_total_time=optimized_time,
            parallel_groups=parallel_groups,
            improvement_percentage=improvement
        )
    
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
