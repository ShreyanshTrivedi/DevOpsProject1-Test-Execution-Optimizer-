"""
Example usage of the Test Execution Optimizer
Demonstrates various features and integration patterns
"""

import json
import time

from test_optimizer import AdvancedTestOptimizer, TestMetrics, OptimizationStrategy

def create_sample_test_suite():
    """Create a sample test suite for demonstration"""
    tests = [
        TestMetrics(
            name="unit_test_auth",
            estimated_time=2.5,
            dependencies=[],
            priority=3,
            resource_usage={"cpu": 1, "memory": 512},
            failure_rate=0.05
        ),
        TestMetrics(
            name="unit_test_database",
            estimated_time=3.0,
            dependencies=[],
            priority=2,
            resource_usage={"cpu": 2, "memory": 1024},
            failure_rate=0.08
        ),
        TestMetrics(
            name="unit_test_api",
            estimated_time=4.0,
            dependencies=["unit_test_auth"],
            priority=2,
            resource_usage={"cpu": 1, "memory": 768},
            failure_rate=0.03
        ),
        TestMetrics(
            name="integration_test_user_flow",
            estimated_time=8.0,
            dependencies=["unit_test_auth", "unit_test_database"],
            priority=1,
            resource_usage={"cpu": 3, "memory": 2048},
            failure_rate=0.12
        ),
        TestMetrics(
            name="integration_test_payment",
            estimated_time=10.0,
            dependencies=["unit_test_auth", "unit_test_api"],
            priority=1,
            resource_usage={"cpu": 2, "memory": 1536},
            failure_rate=0.15
        ),
        TestMetrics(
            name="e2e_test_checkout",
            estimated_time=15.0,
            dependencies=["integration_test_user_flow", "integration_test_payment"],
            priority=1,
            resource_usage={"cpu": 4, "memory": 4096},
            failure_rate=0.20
        ),
        TestMetrics(
            name="performance_test_load",
            estimated_time=25.0,
            dependencies=["integration_test_user_flow"],
            priority=2,
            resource_usage={"cpu": 8, "memory": 8192},
            failure_rate=0.10
        ),
        TestMetrics(
            name="security_test_scan",
            estimated_time=12.0,
            dependencies=[],
            priority=3,
            resource_usage={"cpu": 2, "memory": 2048},
            failure_rate=0.05
        ),
        TestMetrics(
            name="ui_test_smoke",
            estimated_time=6.0,
            dependencies=["unit_test_auth"],
            priority=2,
            resource_usage={"cpu": 3, "memory": 3072},
            failure_rate=0.18
        ),
        TestMetrics(
            name="api_test_compatibility",
            estimated_time=7.0,
            dependencies=["unit_test_api"],
            priority=2,
            resource_usage={"cpu": 2, "memory": 1024},
            failure_rate=0.07
        )
    ]
    return tests

def demonstrate_basic_optimization():
    """Demonstrate basic optimization functionality"""
    print("=== Basic Test Execution Optimization Demo ===\n")
    
    # Create optimizer
    optimizer = AdvancedTestOptimizer()
    
    # Load sample test suite
    tests = create_sample_test_suite()
    optimizer.load_test_suite(tests)
    
    print(f"Loaded {len(tests)} tests")
    print(f"Original total time: {sum(test.estimated_time for test in tests):.1f}s\n")
    
    # Test different optimization strategies
    strategies = [
        OptimizationStrategy.TIME_BASED,
        OptimizationStrategy.PRIORITY_BASED,
        OptimizationStrategy.RESOURCE_BASED,
    ]
    
    for strategy in strategies:
        print(f"--- {strategy.value.upper()} Strategy ---")
        result = optimizer.optimize_with_strategy(strategy, max_parallel=4)
        
        print(f"Optimized order: {result['optimized_order'][:3]}...")
        print(f"Parallel groups: {len(result['parallel_groups'])}")
        print(f"Estimated time: {result['estimated_time']:.1f}s")
        
        original_time = sum(test.estimated_time for test in tests)
        improvement = ((original_time - result['estimated_time']) / original_time) * 100
        print(f"Improvement: {improvement:.1f}%")
        print()

def demonstrate_ci_integration():
    """Demonstrate CI/CD integration capabilities - DEPRECATED"""
    print("=== CI/CD Integration Demo (DEPRECATED) ===\n")
    print("CI/CD integration module has been removed for simplicity.")
    print("To integrate with CI/CD platforms, use the REST API endpoints directly.")
    print()

def demonstrate_api_usage():
    """Demonstrate API usage examples"""
    print("=== API Usage Examples ===\n")
    
    print("1. Optimize Tests via API:")
    print("   curl -X POST 'http://localhost:8000/optimize' \\")
    print("   -H 'Content-Type: application/json' \\")
    print("   -d '{")
    print("     \"tests\": [")
    print("       {")
    print("         \"name\": \"test_auth\",")
    print("         \"estimated_time\": 2.5,")
    print("         \"dependencies\": [],")
    print("         \"priority\": 3")
    print("       }")
    print("     ],")
    print("     \"max_parallel\": 4,")
    print("     \"optimization_strategy\": \"time_based\"")
    print("   }'")
    print()
    
    print("2. Record Execution Results:")
    print("   curl -X POST 'http://localhost:8000/execution/result' \\")
    print("   -H 'Content-Type: application/json' \\")
    print("   -d '{")
    print("     \"test_name\": \"test_auth\",")
    print("     \"actual_time\": 2.3,")
    print("     \"success\": true,")
    print("     \"timestamp\": \"2024-01-01T12:00:00\"")
    print("   }'")
    print()
    
    print("3. View Optimization History:")
    print("   curl -X GET 'http://localhost:8000/execution/history'")
    print()

def create_configuration_example():
    """Create example configuration files"""
    print("=== Configuration Examples ===\n")
    
    # Example test configuration
    test_config = {
        "tests": [
            {
                "name": "authentication_tests",
                "estimated_time": 5.0,
                "dependencies": [],
                "priority": 1,
                "resource_usage": {"cpu": 2, "memory": 1024},
                "tags": ["critical", "security"]
            },
            {
                "name": "database_tests",
                "estimated_time": 8.0,
                "dependencies": [],
                "priority": 2,
                "resource_usage": {"cpu": 3, "memory": 2048},
                "tags": ["integration"]
            },
            {
                "name": "api_tests",
                "estimated_time": 12.0,
                "dependencies": ["authentication_tests"],
                "priority": 1,
                "resource_usage": {"cpu": 2, "memory": 1536},
                "tags": ["integration", "api"]
            }
        ],
        "optimization_settings": {
            "max_parallel": 4,
            "strategy": "time_based",
            "resource_limits": {
                "cpu": 16,
                "memory": 32768
            }
        }
    }
    
    print("Test Configuration (test_config.json):")
    print(json.dumps(test_config, indent=2))
    print()
    
    # Example CI configuration
    ci_config = {
        "github": {
            "repo_owner": "company",
            "repo_name": "project",
            "token": "github-personal-access-token"
        },
        "optimization": {
            "auto_apply": True,
            "backup_original": True,
            "commit_changes": False
        }
    }
    
    print("CI Configuration (ci_config.json):")
    print(json.dumps(ci_config, indent=2))
    print()

def run_performance_benchmark():
    """Run performance benchmark"""
    print("=== Performance Benchmark ===\n")
    
    optimizer = AdvancedTestOptimizer()
    
    # Test with different suite sizes
    suite_sizes = [5, 10, 25, 50, 100]
    
    for size in suite_sizes:
        # Generate test suite
        tests = []
        for i in range(size):
            test = TestMetrics(
                name=f"test_{i}",
                estimated_time=1.0 + (i % 10),
                dependencies=[f"test_{j}" for j in range(max(0, i-3), i) if i > 0 and j % 3 == 0],
                priority=(i % 5) + 1,
                resource_usage={"cpu": 1, "memory": 512}
            )
            tests.append(test)
        
        # Benchmark optimization
        start_time = time.time()
        optimizer.load_test_suite(tests)
        result = optimizer.optimize_with_strategy(OptimizationStrategy.TIME_BASED, max_parallel=4)
        end_time = time.time()
        
        optimization_time = end_time - start_time
        original_time = sum(test.estimated_time for test in tests)
        improvement = ((original_time - result['estimated_time']) / original_time) * 100
        
        print(f"Suite Size: {size:3d} | Optimization Time: {optimization_time:.3f}s | "
              f"Improvement: {improvement:.1f}% | Parallel Groups: {len(result['parallel_groups'])}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Running Test Execution Optimizer Demonstrations")
    print("=" * 50 + "\n")
    
    # Run all demonstrations
    demonstrate_basic_optimization()
    demonstrate_ci_integration()
    demonstrate_api_usage()
    create_configuration_example()
    run_performance_benchmark()
    
    print("=" * 50)
    print("Demo completed! Start the API server with:")
    print("python main.py")
    print("Then visit: http://localhost:8000/static/dashboard.html")
