"""
Advanced Test Execution Optimizer
Core optimization algorithms and ML-based predictions
"""

import networkx as nx
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple, Optional
import json
import time
from dataclasses import dataclass
from enum import Enum

class OptimizationStrategy(Enum):
    TIME_BASED = "time_based"
    PRIORITY_BASED = "priority_based"
    RESOURCE_BASED = "resource_based"
    ML_BASED = "ml_based"
    HYBRID = "hybrid"

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

class MLOptimizer:
    """Machine learning based test time prediction"""
    
    def __init__(self):
        self.time_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.failure_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = ['priority', 'dependency_count', 'cpu_usage', 'memory_usage', 'historical_avg_time']
    
    def extract_features(self, test: TestMetrics, historical_data: Dict[str, List[float]]) -> np.ndarray:
        """Extract features for ML prediction"""
        features = [
            test.priority,
            len(test.dependencies),
            test.resource_usage.get('cpu', 1),
            test.resource_usage.get('memory', 512),
            np.mean(historical_data.get(test.name, [test.estimated_time]))
        ]
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data: List[Tuple[TestMetrics, float]]):
        """Train ML models on historical data"""
        if len(training_data) < 5:
            return False
        
        X = []
        y_time = []
        y_failure = []
        
        for test, actual_time in training_data:
            features = [
                test.priority,
                len(test.dependencies),
                test.resource_usage.get('cpu', 1),
                test.resource_usage.get('memory', 512),
                test.estimated_time
            ]
            X.append(features)
            y_time.append(actual_time)
            y_failure.append(test.failure_rate)
        
        X = np.array(X)
        y_time = np.array(y_time)
        y_failure = np.array(y_failure)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        self.time_model.fit(X_scaled, y_time)
        self.failure_model.fit(X_scaled, y_failure)
        self.is_trained = True
        
        return True
    
    def predict_execution_time(self, test: TestMetrics) -> float:
        """Predict test execution time"""
        if not self.is_trained:
            return test.estimated_time
        
        features = [
            test.priority,
            len(test.dependencies),
            test.resource_usage.get('cpu', 1),
            test.resource_usage.get('memory', 512),
            test.estimated_time
        ]
        
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        predicted_time = self.time_model.predict(X_scaled)[0]
        return max(0.1, predicted_time)  # Ensure positive time
    
    def predict_failure_probability(self, test: TestMetrics) -> float:
        """Predict test failure probability"""
        if not self.is_trained:
            return test.failure_rate
        
        features = [
            test.priority,
            len(test.dependencies),
            test.resource_usage.get('cpu', 1),
            test.resource_usage.get('memory', 512),
            test.estimated_time
        ]
        
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        return max(0.0, min(1.0, self.failure_model.predict(X_scaled)[0]))

class AdvancedTestOptimizer:
    """Advanced test execution optimizer with multiple strategies"""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.ml_optimizer = MLOptimizer()
        self.execution_history = []
        self.historical_data = {}
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
    
    def train_ml_models(self):
        """Train ML models with historical data"""
        if len(self.execution_history) >= 5:
            training_data = []
            for record in self.execution_history:
                test_name = record['test']
                if test_name in self.dependency_graph.nodes:
                    test_node = self.dependency_graph.nodes[test_name]['test']
                    training_data.append((test_node, record['actual_time']))
            
            self.ml_optimizer.train(training_data)
    
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
        elif strategy == OptimizationStrategy.ML_BASED:
            result = self._optimize_ml_based(max_parallel)
        elif strategy == OptimizationStrategy.HYBRID:
            result = self._optimize_hybrid(max_parallel)
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
    
    def _optimize_ml_based(self, max_parallel: int) -> Dict:
        """ML-based optimization using predicted times and failure rates"""
        # Update times with ML predictions
        for test_name in self.dependency_graph.nodes:
            test_node = self.dependency_graph.nodes[test_name]['test']
            predicted_time = self.ml_optimizer.predict_execution_time(test_node)
            self.dependency_graph.nodes[test_name]['time'] = predicted_time
            
            # Consider failure probability in priority
            failure_prob = self.ml_optimizer.predict_failure_probability(test_node)
            adjusted_priority = test_node.priority * (1 + failure_prob * 0.5)  # Increase priority for failure-prone tests
            self.dependency_graph.nodes[test_name]['priority'] = adjusted_priority
        
        # Use hybrid approach with ML-enhanced data
        return self._optimize_hybrid(max_parallel)
    
    def _optimize_hybrid(self, max_parallel: int) -> Dict:
        """Hybrid optimization combining multiple factors"""
        optimized_order = list(nx.topological_sort(self.dependency_graph))
        
        # Calculate composite score for each test
        levels = self._get_dependency_levels()
        for level in levels:
            level_tests = levels[level]
            level_tests.sort(key=lambda x: self._calculate_composite_score(x))
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
            'strategy': 'hybrid'
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
    
    def _calculate_composite_score(self, test_name: str) -> float:
        """Calculate composite optimization score"""
        node_data = self.dependency_graph.nodes[test_name]
        
        # Factors: time (lower is better), priority (higher is better), failure rate (higher is better for early detection)
        time_score = 1 / (node_data['time'] + 0.1)  # Avoid division by zero
        priority_score = node_data['priority'] / 10  # Normalize to 0-1
        failure_score = node_data.get('failure_rate', 0) * 2  # Weight failure detection
        
        return time_score + priority_score + failure_score
    
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
        """Record test execution result for learning"""
        self.execution_history.append({
            'test': test_name,
            'actual_time': actual_time,
            'success': success,
            'timestamp': time.time()
        })
        
        # Update historical data
        if test_name not in self.historical_data:
            self.historical_data[test_name] = []
        self.historical_data[test_name].append(actual_time)
        
        # Keep only last 50 executions per test
        if len(self.historical_data[test_name]) > 50:
            self.historical_data[test_name] = self.historical_data[test_name][-50:]
        
        # Retrain ML models periodically
        if len(self.execution_history) % 10 == 0:
            self.train_ml_models()
    
    def get_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report"""
        if not self.dependency_graph.nodes:
            return {"error": "No test suite loaded"}
        
        # Test different strategies
        strategies = [OptimizationStrategy.TIME_BASED, OptimizationStrategy.PRIORITY_BASED, 
                     OptimizationStrategy.HYBRID]
        
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
            'ml_trained': self.ml_optimizer.is_trained
        }
