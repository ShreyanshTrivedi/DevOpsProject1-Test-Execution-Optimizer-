# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the Test Execution Optimizer.

## Prerequisites

- Kubernetes cluster (minikube, kind, EKS, GKE, AKS)
- kubectl configured
- Docker image built and pushed to registry

## Quick Start

### Using kubectl

```bash
# Apply all manifests
kubectl apply -f .

# Or apply specific files
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Using Kustomize

```bash
# Apply with kustomize
kubectl apply -k .

# Preview changes
kubectl apply -k . --dry-run=client
```

## Files

| File | Description |
|------|-------------|
| namespace.yaml | Namespace, ResourceQuota, LimitRange |
| configmap.yaml | ConfigMap and Secret definitions |
| deployment.yaml | Deployment with 2 replicas |
| service.yaml | ClusterIP and LoadBalancer services |
| hpa.yaml | HorizontalPodAutoscaler |
| ingress.yaml | NGINX Ingress configuration |
| kustomization.yaml | Kustomize configuration |

## Configuration

### Update Image

Edit `deployment.yaml` and update the image:
```yaml
containers:
  - name: test-optimizer
    image: your-registry/test-optimizer:v1.0.0
```

Or with kustomization:
```yaml
images:
  - name: test-optimizer
    newName: your-registry/test-optimizer
    newTag: v1.0.0
```

## Verify Deployment

```bash
# Check pods
kubectl get pods -l app=test-optimizer

# Check services
kubectl get svc test-optimizer

# Check deployment
kubectl get deployment test-optimizer

# View logs
kubectl logs -l app=test-optimizer

# Describe deployment
kubectl describe deployment test-optimizer
```

## Scaling

### Manual Scaling
```bash
kubectl scale deployment test-optimizer --replicas=5
```

### Auto Scaling (HPA)
The HPA is configured to scale between 2-10 replicas based on:
- CPU utilization: 70%
- Memory utilization: 80%

## Clean Up

```bash
kubectl delete -f .
# Or with kustomize
kubectl delete -k .
```

## Production Considerations

1. Update secrets in configmap.yaml with actual values
2. Configure TLS certificates in ingress.yaml
3. Set up persistent storage if needed
4. Configure monitoring and logging
5. Review resource limits for your cluster