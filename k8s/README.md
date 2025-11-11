# Kubernetes Deployment Manifests

This directory contains Kubernetes manifests for deploying the SureFinance application.

## Files

- `backend-deployment.yaml` - Backend FastAPI deployment
- `backend-service.yaml` - Backend service (ClusterIP)
- `frontend-deployment.yaml` - Frontend React deployment
- `frontend-service.yaml` - Frontend service (LoadBalancer)
- `ingress.yaml` - Ingress configuration for external access

## Quick Start

### Prerequisites

1. Kubernetes cluster running
2. kubectl configured to access your cluster
3. Docker images pushed to Docker Hub

### Deployment Steps

1. **Update Docker Hub username in manifests:**
   ```bash
   # Replace DOCKER_USERNAME with your Docker Hub username
   sed -i 's/DOCKER_USERNAME/your-username/g' k8s/*.yaml
   ```

2. **Apply manifests:**
   ```bash
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/backend-service.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   kubectl apply -f k8s/frontend-service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

3. **Check deployment status:**
   ```bash
   kubectl get deployments
   kubectl get services
   kubectl get pods
   kubectl get ingress
   ```

4. **Access the application:**
   - If using LoadBalancer: `kubectl get services` to get external IP
   - If using Ingress: Update `/etc/hosts` with ingress hostname or use the ingress IP

## Configuration

### Backend Deployment

- **Replicas:** 2
- **Resources:**
  - Requests: 256Mi memory, 250m CPU
  - Limits: 512Mi memory, 500m CPU
- **Port:** 8000
- **Health Checks:** Liveness and readiness probes configured

### Frontend Deployment

- **Replicas:** 2
- **Resources:**
  - Requests: 128Mi memory, 100m CPU
  - Limits: 256Mi memory, 200m CPU
- **Port:** 80
- **Health Checks:** Liveness and readiness probes configured

### Services

- **Backend Service:** ClusterIP (internal access only)
- **Frontend Service:** LoadBalancer (external access)
- **Ingress:** Routes traffic to frontend and backend based on path

## Customization

### Update Image Tags

To use a specific image tag instead of `latest`:

```bash
sed -i 's/:latest/:v1.0.0/g' k8s/*-deployment.yaml
```

### Scale Deployments

```bash
kubectl scale deployment backend-deployment --replicas=3
kubectl scale deployment frontend-deployment --replicas=3
```

### Update Resources

Edit the `resources` section in deployment files to adjust CPU and memory limits.

### Environment Variables

Add environment variables to deployments:

```yaml
env:
- name: ENV_VAR_NAME
  value: "value"
```

## Troubleshooting

### Check Pod Logs

```bash
kubectl logs <pod-name>
kubectl logs -f deployment/backend-deployment
kubectl logs -f deployment/frontend-deployment
```

### Describe Resources

```bash
kubectl describe deployment backend-deployment
kubectl describe pod <pod-name>
kubectl describe service backend-service
```

### Port Forward (for testing)

```bash
# Backend
kubectl port-forward service/backend-service 8000:8000

# Frontend
kubectl port-forward service/frontend-service 8080:80
```

### Delete and Redeploy

```bash
kubectl delete -f k8s/
kubectl apply -f k8s/
```

## Notes

- The ingress configuration requires an ingress controller (e.g., nginx-ingress)
- For production, consider using a managed Kubernetes service (EKS, GKE, AKS)
- Update CORS settings in backend for production domains
- Consider using ConfigMaps and Secrets for configuration management
- Set up monitoring and logging for production deployments


