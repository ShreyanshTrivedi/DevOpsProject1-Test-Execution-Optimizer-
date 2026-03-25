"""
CI/CD Integration Modules for Test Execution Optimizer
Supports GitHub Actions
"""

import json
import requests
import os
from typing import Dict, List, Any
from abc import ABC, abstractmethod

class CIIntegration(ABC):
    """Abstract base class for CI/CD integrations"""
    
    @abstractmethod
    def get_test_suite(self) -> List[Dict]:
        """Extract test suite information from CI configuration"""
        ...
    
    @abstractmethod
    def apply_optimization(self, optimized_order: List[str]) -> bool:
        """Apply optimized test order to CI pipeline"""
        ...
    
    @abstractmethod
    def get_execution_history(self) -> List[Dict]:
        """Get historical test execution data"""
        ...

class GitHubActionsIntegration(CIIntegration):
    """GitHub Actions integration"""
    
    def __init__(self, repo_owner: str, repo_name: str, token: str = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token
        self.headers = {'Authorization': f'token {token}'} if token else {}
    
    def get_test_suite(self) -> List[Dict]:
        """Extract test suite from GitHub Actions workflow files"""
        try:
            # Get workflow files
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/.github/workflows"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            workflows = response.json()
            tests = []
            
            for workflow in workflows:
                if workflow['name'].endswith('.yml') or workflow['name'].endswith('.yaml'):
                    # Get workflow content
                    workflow_url = workflow['url']
                    workflow_response = requests.get(workflow_url, headers=self.headers)
                    workflow_response.raise_for_status()
                    
                    workflow_content = workflow_response.json()
                    workflow_yaml = workflow_content.get('content', '')
                    
                    # Parse test commands (simplified)
                    if 'pytest' in workflow_yaml:
                        tests.append({
                            'name': f"github_workflow_{workflow['name']}",
                            'estimated_time': 10.0,
                            'dependencies': [],
                            'priority': 1
                        })
            
            return tests
            
        except Exception as e:
            print(f"Error getting GitHub Actions test suite: {e}")
            return []
    
    def apply_optimization(self, optimized_order: List[str]) -> bool:
        """Apply optimization to GitHub Actions workflow"""
        try:
            # Create optimized workflow step
            workflow_step = {
                'name': 'Run Optimized Tests',
                'run': ' && '.join([f"pytest {test}" for test in optimized_order])
            }
            
            # Save optimization to file
            with open('github_optimization.json', 'w') as f:
                json.dump({
                    'optimized_order': optimized_order,
                    'workflow_step': workflow_step
                }, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error applying GitHub Actions optimization: {e}")
            return False
    
    def get_execution_history(self) -> List[Dict]:
        """Get workflow run history"""
        try:
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            runs_data = response.json()
            history = []
            
            for run in runs_data.get('workflow_runs', [])[:10]:  # Last 10 runs
                history.append({
                    'timestamp': run['created_at'],
                    'duration': run['run_duration'],
                    'status': run['conclusion']
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting GitHub Actions history: {e}")
            return []

class CIIntegrationManager:
    """Manager for all CI/CD integrations"""
    
    def __init__(self):
        self.integrations = {}
    
    def register_integration(self, name: str, integration: CIIntegration):
        """Register a CI integration"""
        self.integrations[name] = integration
    
    def get_integration(self, name: str) -> CIIntegration:
        """Get a specific integration"""
        return self.integrations.get(name)
    
    def list_integrations(self) -> List[str]:
        """List all registered integrations"""
        return list(self.integrations.keys())
    
    def auto_detect_ci(self) -> List[str]:
        """Auto-detect available CI systems"""
        detected = []
        
        # Check for GitHub Actions
        if os.path.exists('.github/workflows'):
            detected.append('github_actions')
        
        return detected

def create_github_integration(repo_owner: str, repo_name: str, token: str = None):
    """Factory function for GitHub Actions integration"""
    return GitHubActionsIntegration(repo_owner, repo_name, token)

# Initialize global CI manager
ci_manager = CIIntegrationManager()
