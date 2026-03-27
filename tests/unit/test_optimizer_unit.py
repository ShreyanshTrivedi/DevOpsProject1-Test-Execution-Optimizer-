"""
Unit Tests for Test Execution Optimizer
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_optimizer import (
    AdvancedTestOptimizer,
    TestMetrics,
    OptimizationStrategy
)


class TestTestMetrics:
    """Test the TestMetrics dataclass"""

    def test_create_test_metrics(self):
        """Test creating a TestMetrics object"""
        test = TestMetrics(
            name="test_example",
            estimated_time=5.0,
            dependencies=["test_dependency"],
            priority=3,
            resource_usage={"cpu": 2, "memory": 1024}
        )

        assert test.name == "test_example"
        assert test.estimated_time == 5.0
        assert test.dependencies == ["test_dependency"]
        assert test.priority == 3
        assert test.resource_usage == {"cpu": 2, "memory": 1024}

    def test_default_values(self):
        """Test default values for TestMetrics"""
        test = TestMetrics(name="test_simple", estimated_time=2.0)

        assert test.dependencies == []
        assert test.priority == 1
        assert test.resource_usage == {}
        assert test.failure_rate == 0.0


class TestAdvancedTestOptimizer:
    """Test the AdvancedTestOptimizer class"""

    def test_create_optimizer(self):
        """Test creating an optimizer instance"""
        optimizer = AdvancedTestOptimizer()
        assert optimizer is not None
        assert optimizer.dependency_graph is not None

    def test_load_test_suite(self):
        """Test loading a test suite"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="test1", estimated_time=2.0),
            TestMetrics(name="test2", estimated_time=3.0, dependencies=["test1"]),
            TestMetrics(name="test3", estimated_time=1.5, dependencies=["test1"]),
        ]

        optimizer.load_test_suite(tests)
        assert len(optimizer.dependency_graph.nodes) == 3

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="test1", estimated_time=2.0, dependencies=["test2"]),
            TestMetrics(name="test2", estimated_time=3.0, dependencies=["test1"]),
        ]

        with pytest.raises(ValueError, match="Circular dependencies"):
            optimizer.load_test_suite(tests)

    def test_time_based_optimization(self):
        """Test time-based optimization strategy"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="slow_test", estimated_time=10.0),
            TestMetrics(name="fast_test", estimated_time=1.0),
            TestMetrics(name="medium_test", estimated_time=5.0),
        ]

        optimizer.load_test_suite(tests)
        result = optimizer.optimize_with_strategy(OptimizationStrategy.TIME_BASED, max_parallel=2)

        assert "optimized_order" in result
        assert "parallel_groups" in result
        assert result["strategy"] == "time_based"

    def test_priority_based_optimization(self):
        """Test priority-based optimization strategy"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="test1", estimated_time=5.0, priority=1),
            TestMetrics(name="test2", estimated_time=5.0, priority=10),
            TestMetrics(name="test3", estimated_time=5.0, priority=5),
        ]

        optimizer.load_test_suite(tests)
        result = optimizer.optimize_with_strategy(OptimizationStrategy.PRIORITY_BASED, max_parallel=2)

        assert result["strategy"] == "priority_based"
        # Higher priority should come first
        assert result["optimized_order"][0] == "test2"

    def test_resource_based_optimization(self):
        """Test resource-based optimization strategy"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="test1", estimated_time=2.0, resource_usage={"cpu": 2, "memory": 1024}),
            TestMetrics(name="test2", estimated_time=3.0, resource_usage={"cpu": 1, "memory": 512}),
        ]

        optimizer.load_test_suite(tests)
        result = optimizer.optimize_with_strategy(OptimizationStrategy.RESOURCE_BASED, max_parallel=2)

        assert result["strategy"] == "resource_based"
        assert len(result["optimized_order"]) == 2

    def test_parallel_groups_creation(self):
        """Test creating parallel execution groups"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="test1", estimated_time=2.0, resource_usage={"cpu": 1, "memory": 512}),
            TestMetrics(name="test2", estimated_time=3.0, resource_usage={"cpu": 1, "memory": 512}),
        ]

        optimizer.load_test_suite(tests)
        result = optimizer.optimize_with_strategy(OptimizationStrategy.TIME_BASED, max_parallel=2)

        assert len(result["parallel_groups"]) >= 1

    def test_execution_result_recording(self):
        """Test recording execution results"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="test1", estimated_time=2.0),
        ]

        optimizer.load_test_suite(tests)
        optimizer.record_execution_result("test1", 2.5, True)

        assert len(optimizer.execution_history) == 1
        assert optimizer.execution_history[0]["actual_time"] == 2.5

    def test_optimization_report(self):
        """Test generating optimization report"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="test1", estimated_time=2.0, priority=3),
            TestMetrics(name="test2", estimated_time=3.0, priority=5),
        ]

        optimizer.load_test_suite(tests)
        report = optimizer.get_optimization_report()

        assert "test_count" in report
        assert report["test_count"] == 2
        assert "strategy_comparison" in report


class TestOptimizationStrategies:
    """Test all optimization strategies"""

    @pytest.mark.parametrize("strategy", [
        OptimizationStrategy.TIME_BASED,
        OptimizationStrategy.PRIORITY_BASED,
        OptimizationStrategy.RESOURCE_BASED,
    ])
    def test_all_strategies(self, strategy):
        """Test that all strategies work"""
        optimizer = AdvancedTestOptimizer()

        tests = [
            TestMetrics(name="test1", estimated_time=2.0, priority=3,
                      resource_usage={"cpu": 1, "memory": 512}),
            TestMetrics(name="test2", estimated_time=3.0, priority=5,
                      resource_usage={"cpu": 2, "memory": 1024}),
        ]

        optimizer.load_test_suite(tests)
        result = optimizer.optimize_with_strategy(strategy, max_parallel=2)

        assert "optimized_order" in result
        assert "parallel_groups" in result
        assert len(result["optimized_order"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])