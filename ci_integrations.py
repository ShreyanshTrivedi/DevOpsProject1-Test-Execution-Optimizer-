"""
CI/CD Integration Modules for Test Execution Optimizer
Supports Jenkins, GitHub Actions, GitLab CI, and Azure DevOps
"""

import json
import requests
import subprocess
import os
from typing import Dict, List, Any
from abc import ABC, abstractmethod

class CIIntegration(ABC):
    """Abstract base class for CI/CD integrations"""
    
    @abstractmethod
    def get_test_suite(self) -> List[Dict]:
        """Extract test suite information from CI configuration"""
        pass
    
    @abstractmethod
    def apply_optimization(self, optimized_order: List[str]) -> bool:
        """Apply optimized test order to CI pipeline"""
        pass
    
    @abstractmethod
    def get_execution_history(self) -> List[Dict]:
        """Get historical test execution data"""
        pass

class JenkinsIntegration(CIIntegration):
    """Jenkins CI integration"""
    
    def __init__(self, jenkins_url: str, job_name: str, username: str = None, password: str = None):
        self.jenkins_url = jenkins_url.rstrip('/')
        self.job_name = job_name
        self.username = username
        self.password = password
        self.auth = (username, password) if username and password else None
    
    def get_test_suite(self) -> List[Dict]:
        """Extract test suite from Jenkins job configuration"""
        try:
            # Get job config
            config_url = f"{self.jenkins_url}/job/{self.job_name}/config.xml"
            response = requests.get(config_url, auth=self.auth)
            response.raise_for_status()
            
            # Parse test commands from config (simplified)
            tests = []
            config_xml = response.text
            
            # Extract pytest commands
            if "pytest" in config_xml:
                # This is a simplified parser - in real implementation, use proper XML parsing
                test_files = []
                for line in config_xml.split('\n'):
                    if 'test_' in line and '.py' in line:
                        test_files.append(line.strip())
                
                for test_file in test_files:
                    tests.append({
                        'name': test_file,
                        'estimated_time': 5.0,  # Default estimate
                        'dependencies': [],
                        'priority': 1
                    })
            
            return tests
        
        except Exception as e:
            print(f"Error getting Jenkins test suite: {e}")
            return []
    
    def apply_optimization(self, optimized_order: List[str]) -> bool:
        """Apply optimized order to Jenkins pipeline"""
        try:
            # Create optimized test script
            test_script = "#!/bin/bash\n"
            test_script += "# Optimized test execution order\n"
            test_script += "echo 'Running optimized test suite...'\n"
            
            for test_name in optimized_order:
                test_script += f"echo 'Running {test_name}...'\n"
                test_script += f"pytest {test_name} --junitxml=results/{test_name}.xml\n"
            
            # Save script to workspace
            script_path = "optimized_tests.sh"
            with open(script_path, 'w') as f:
                f.write(test_script)
            
            os.chmod(script_path, 0o755)
            return True
            
        except Exception as e:
            print(f"Error applying Jenkins optimization: {e}")
            return False
    
    def get_execution_history(self) -> List[Dict]:
        """Get test execution history from Jenkins"""
        try:
            # Get last build results
            build_url = f"{self.jenkins_url}/job/{self.job_name}/lastBuild/api/json"
            response = requests.get(build_url, auth=self.auth)
            response.raise_for_status()
            
            build_data = response.json()
            history = []
            
            # Parse test results (simplified)
            if build_data.get('result') == 'SUCCESS':
                history.append({
                    'timestamp': build_data['timestamp'],
                    'duration': build_data['duration'],
                    'status': 'success'
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting Jenkins history: {e}")
            return []

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

class GitLabCIIntegration(CIIntegration):
    """GitLab CI integration"""
    
    def __init__(self, project_id: str, token: str = None, gitlab_url: str = "https://gitlab.com"):
        self.project_id = project_id
        self.token = token
        self.gitlab_url = gitlab_url.rstrip('/')
        self.headers = {'PRIVATE-TOKEN': token} if token else {}
    
    def get_test_suite(self) -> List[Dict]:
        """Extract test suite from GitLab CI configuration"""
        try:
            # Get .gitlab-ci.yml content
            api_url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/repository/files/.gitlab-ci.yml/raw"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            ci_config = response.text
            tests = []
            
            # Parse test jobs (simplified)
            if 'test' in ci_config:
                for line in ci_config.split('\n'):
                    if line.strip().startswith('test_'):
                        job_name = line.strip().replace(':', '')
                        tests.append({
                            'name': job_name,
                            'estimated_time': 8.0,
                            'dependencies': [],
                            'priority': 1
                        })
            
            return tests
            
        except Exception as e:
            print(f"Error getting GitLab CI test suite: {e}")
            return []
    
    def apply_optimization(self, optimized_order: List[str]) -> bool:
        """Apply optimization to GitLab CI"""
        try:
            # Create optimized .gitlab-ci.yml
            optimized_config = "# Optimized GitLab CI Configuration\n"
            optimized_config += "stages:\n  - test\n\n"
            
            # Create needs dependencies
            previous_job = None
            for i, test_name in enumerate(optimized_order):
                job_config = f"{test_name}:\n"
                job_config += "  stage: test\n"
                job_config += f"  script:\n    - pytest {test_name}\n"
                
                if previous_job:
                    job_config += f"  needs:\n    - {previous_job}\n"
                
                optimized_config += job_config + "\n"
                previous_job = test_name
            
            # Save optimized config
            with open('.gitlab-ci-optimized.yml', 'w') as f:
                f.write(optimized_config)
            
            return True
            
        except Exception as e:
            print(f"Error applying GitLab CI optimization: {e}")
            return False
    
    def get_execution_history(self) -> List[Dict]:
        """Get pipeline history"""
        try:
            api_url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/pipelines"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            pipelines = response.json()
            history = []
            
            for pipeline in pipelines[:10]:  # Last 10 pipelines
                history.append({
                    'timestamp': pipeline['created_at'],
                    'duration': pipeline.get('duration', 0),
                    'status': pipeline['status']
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting GitLab CI history: {e}")
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
        
        # Check for Jenkins
        if os.path.exists('Jenkinsfile'):
            detected.append('jenkins')
        
        # Check for GitHub Actions
        if os.path.exists('.github/workflows'):
            detected.append('github_actions')
        
        # Check for GitLab CI
        if os.path.exists('.gitlab-ci.yml'):
            detected.append('gitlab_ci')
        
        # Check for Azure DevOps
        if os.path.exists('azure-pipelines.yml'):
            detected.append('azure_devops')
        
        return detected

# Example usage and factory functions
def create_jenkins_integration(jenkins_url: str, job_name: str, username: str = None, password: str = None):
    """Factory function for Jenkins integration"""
    return JenkinsIntegration(jenkins_url, job_name, username, password)

def create_github_integration(repo_owner: str, repo_name: str, token: str = None):
    """Factory function for GitHub Actions integration"""
    return GitHubActionsIntegration(repo_owner, repo_name, token)

def create_gitlab_integration(project_id: str, token: str = None, gitlab_url: str = "https://gitlab.com"):
    """Factory function for GitLab CI integration"""
    return GitLabCIIntegration(project_id, token, gitlab_url)

# Initialize global CI manager
ci_manager = CIIntegrationManager()
