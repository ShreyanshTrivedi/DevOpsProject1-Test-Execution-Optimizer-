"""
Advanced Test Execution Optimizer
Core optimization algorithms
"""

import networkx as nx
from typing import List, Dict, Optional
import time

from dataclasses import dataclass
from enum import Enum

class OptimizationStrategy(Enum):
    TIME_BASED = "time_based"
    PRIORITY_BASED = "priority_based"
    RESOURCE_BASED = "resource_based"

@dataclass
class TestMetrics:
    name: str
    estimated_time: float
    actual_time: Optional[float] = None
    dependencies: List[str] = None
    priority: int = 1
    resource_usage: Dict[str, float] = None
    failure_rate: float = 0.0
    last_execution: Optional[float] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.resource_usage is None:
            self.resource_usage = {}

class AdvancedTestOptimizer:
    """Advanced test execution optimizer with multiple strategies"""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.execution_history = []
        self.optimization_cache = {}
    
    def load_test_suite(self, tests: List[TestMetrics]):
        """Load test suite and build dependency graph"""
        self.dependency_graph.clear()
        
        for test in tests:
            self.dependency_graph.add_node(
                test.name,
                test=test,
                time=test.estimated_time,
                priority=test.priority,
                resources=test.resource_usage,
                failure_rate=test.failure_rate
            )
            
            for dep in test.dependencies:
                self.dependency_graph.add_edge(dep, test.name)
        
        # Validate dependency graph
        if not nx.is_directed_acyclic_graph(self.dependency_graph):
            raise ValueError("Circular dependencies detected in test suite")
    
    def optimize_with_strategy(self, strategy: OptimizationStrategy, max_parallel: int = 4) -> Dict:
        """Optimize test execution using specified strategy"""
        cache_key = f"{strategy.value}_{max_parallel}"
        if cache_key in self.optimization_cache:
            return self.optimization_cache[cache_key]
        
        if strategy == OptimizationStrategy.TIME_BASED:
            result = self._optimize_time_based(max_parallel)
        elif strategy == OptimizationStrategy.PRIORITY_BASED:
            result = self._optimize_priority_based(max_parallel)
        elif strategy == OptimizationStrategy.RESOURCE_BASED:
            result = self._optimize_resource_based(max_parallel)
        else:
            result = self._optimize_time_based(max_parallel)
        
        self.optimization_cache[cache_key] = result
        return result
    
    def _optimize_time_based(self, max_parallel: int) -> Dict:
        """Time-based optimization: prioritize faster tests first"""
        optimized_order = list(nx.topological_sort(self.dependency_graph))
        
        # Sort by estimated time within each dependency level
        levels = self._get_dependency_levels()
        for level in levels:
            level_tests = levels[level]
            level_tests.sort(key=lambda x: self.dependency_graph.nodes[x]['time'])
            levels[level] = level_tests
        
        # Reconstruct order
        final_order = []
        for level in sorted(levels.keys()):
            final_order.extend(levels[level])
        
        parallel_groups = self._create_parallel_groups(final_order, max_parallel)
        
        return {
            'optimized_order': final_order,
            'parallel_groups': parallel_groups,
            'estimated_time': self._calculate_total_time(parallel_groups),
            'strategy': 'time_based'
        }
    
    def _optimize_priority_based(self, max_parallel: int) -> Dict:
        """Priority-based optimization: prioritize high-priority tests"""
        optimized_order = list(nx.topological_sort(self.dependency_graph))
        
        # Sort by priority (descending) within each dependency level
        levels = self._get_dependency_levels()
        for level in levels:
            level_tests = levels[level]
            level_tests.sort(key=lambda x: self.dependency_graph.nodes[x]['priority'], reverse=True)
            levels[level] = level_tests
        
        # Reconstruct order
        final_order = []
        for level in sorted(levels.keys()):
            final_order.extend(levels[level])
        
        parallel_groups = self._create_parallel_groups(final_order, max_parallel)
        
        return {
            'optimized_order': final_order,
            'parallel_groups': parallel_groups,
            'estimated_time': self._calculate_total_time(parallel_groups),
            'strategy': 'priority_based'
        }
    
    def _optimize_resource_based(self, max_parallel: int) -> Dict:
        """Resource-based optimization: balance resource usage"""
        optimized_order = list(nx.topological_sort(self.dependency_graph))
        
        # Sort by resource efficiency (lower resource usage first)
        levels = self._get_dependency_levels()
        for level in levels:
            level_tests = levels[level]
            level_tests.sort(key=lambda x: self._calculate_resource_score(x))
            levels[level] = level_tests
        
        # Reconstruct order
        final_order = []
        for level in sorted(levels.keys()):
            final_order.extend(levels[level])
        
        parallel_groups = self._create_parallel_groups(final_order, max_parallel)
        
        return {
            'optimized_order': final_order,
            'parallel_groups': parallel_groups,
            'estimated_time': self._calculate_total_time(parallel_groups),
            'strategy': 'resource_based'
        }
    
    def _get_dependency_levels(self) -> Dict[int, List[str]]:
        """Group tests by dependency level"""
        levels = {}
        for node in self.dependency_graph.nodes():
            if list(self.dependency_graph.predecessors(node)):
                # Calculate level based on longest path from any root
                max_level = 0
                for pred in self.dependency_graph.predecessors(node):
                    pred_level = max([k for k, v in levels.items() if pred in v] or [0])
                    max_level = max(max_level, pred_level + 1)
                level = max_level
            else:
                level = 0
            
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
        
        return levels
    
    def _calculate_resource_score(self, test_name: str) -> float:
        """Calculate resource efficiency score"""
        node_data = self.dependency_graph.nodes[test_name]
        resources = node_data['resources']
        time = node_data['time']
        
        # Lower resource usage per unit time is better
        cpu_score = resources.get('cpu', 1) / time
        memory_score = resources.get('memory', 512) / time / 1024  # Convert to GB
        
        return cpu_score + memory_score
    
    def _create_parallel_groups(self, test_order: List[str], max_parallel: int) -> List[List[str]]:
        """Create parallel execution groups"""
        parallel_groups = []
        remaining_tests = test_order.copy()
        
        while remaining_tests:
            current_group = []
            current_resources = {"cpu": 0, "memory": 0}
            
            for test in remaining_tests[:]:
                test_resources = self.dependency_graph.nodes[test]['resources']
                test_cpu = test_resources.get('cpu', 1)
                test_memory = test_resources.get('memory', 512)
                
                # Check if test can run in parallel
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
                    current_resources["memory"] + test_memory <= max_parallel * 2048):
                    
                    current_group.append(test)
                    current_resources["cpu"] += test_cpu
                    current_resources["memory"] += test_memory
                    remaining_tests.remove(test)
            
            if current_group:
                parallel_groups.append(current_group)
            else:
                # Force execution if no tests can be parallelized
                parallel_groups.append([remaining_tests.pop(0)])
        
        return parallel_groups
    
    def _calculate_total_time(self, parallel_groups: List[List[str]]) -> float:
        """Calculate total execution time for parallel groups"""
        total_time = 0
        for group in parallel_groups:
            group_time = max(self.dependency_graph.nodes[test]['time'] for test in group) if group else 0
            total_time += group_time
        return total_time
    
    def record_execution_result(self, test_name: str, actual_time: float, success: bool):
        """Record test execution result"""
        self.execution_history.append({
            'test': test_name,
            'actual_time': actual_time,
            'success': success,
            'timestamp': time.time()
        })
    
    def get_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report"""
        if not self.dependency_graph.nodes:
            return {"error": "No test suite loaded"}
        
        # Test different strategies
        strategies = [
            OptimizationStrategy.TIME_BASED,
            OptimizationStrategy.PRIORITY_BASED,
            OptimizationStrategy.RESOURCE_BASED,
        ]
        
        results = {}
        original_time = sum(self.dependency_graph.nodes[node]['time'] for node in self.dependency_graph.nodes())
        
        for strategy in strategies:
            result = self.optimize_with_strategy(strategy, max_parallel=4)
            improvement = ((original_time - result['estimated_time']) / original_time) * 100
            results[strategy.value] = {
                'estimated_time': result['estimated_time'],
                'improvement_percentage': improvement,
                'parallel_groups': len(result['parallel_groups'])
            }
        
        return {
            'test_count': len(self.dependency_graph.nodes()),
            'original_time': original_time,
            'strategy_comparison': results,
            'historical_executions': len(self.execution_history),
            'ml_trained': False
        }
