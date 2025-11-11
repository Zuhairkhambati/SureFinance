# CI/CD Pipeline Setup Guide

This guide will help you set up a complete CI/CD pipeline using GitHub Actions, Docker Hub, and Kubernetes for the SureFinance project.

## 📋 Prerequisites

1. **GitHub Account** with a repository
2. **Docker Hub Account** (create at https://hub.docker.com/)
3. **Kubernetes Cluster** (can be local with Minikube, cloud-based like AWS EKS, GKE, AKS, or local cluster)
4. **kubectl** installed and configured to access your cluster

## 🔐 Setting up GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

### Required Secrets:

1. **DOCKER_USERNAME**
   - Your Docker Hub username
   - Example: `myusername`

2. **DOCKER_PASSWORD**
   - Your Docker Hub password or access token
   - For better security, use an access token (Docker Hub → Account Settings → Security → New Access Token)

3. **KUBE_CONFIG**
   - Your Kubernetes config file encoded in base64
   - To get it, run:
     ```bash
     cat ~/.kube/config | base64 -w 0
     ```
   - On Windows (PowerShell):
     ```powershell
     [Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.kube\config"))
     ```

## 🐳 Docker Hub Setup

1. Create a Docker Hub account at https://hub.docker.com/
2. Create two repositories:
   - `surefinance-backend`
   - `surefinance-frontend`

3. Update the Kubernetes manifests:
   - Open `k8s/backend-deployment.yaml`
   - Replace `DOCKER_USERNAME` with your Docker Hub username
   - Open `k8s/frontend-deployment.yaml`
   - Replace `DOCKER_USERNAME` with your Docker Hub username

   Or, let the GitHub Actions workflow handle it automatically (it will replace `DOCKER_USERNAME` during deployment).

## ☸️ Kubernetes Setup

### Option 1: Local Setup with Minikube

1. Install Minikube:
   ```bash
   # macOS/Linux
   brew install minikube
   
   # Or download from https://minikube.sigs.k8s.io/docs/start/
   ```

2. Start Minikube:
   ```bash
   minikube start
   ```

3. Enable ingress (if using ingress):
   ```bash
   minikube addons enable ingress
   ```

4. Get Minikube IP:
   ```bash
   minikube ip
   ```

### Option 2: Cloud Kubernetes (AWS EKS, GKE, AKS)

1. Create a Kubernetes cluster on your preferred cloud provider
2. Configure `kubectl` to connect to your cluster
3. Get your kubeconfig and encode it to base64 for GitHub secrets

### Option 3: Docker Desktop Kubernetes

1. Enable Kubernetes in Docker Desktop settings
2. Wait for Kubernetes to start
3. Use the default context: `docker-desktop`

## 📝 Updating Kubernetes Manifests

Before deploying, update the image names in the Kubernetes manifests:

### Manual Update:

1. Edit `k8s/backend-deployment.yaml`:
   ```yaml
   image: YOUR_DOCKER_USERNAME/surefinance-backend:latest
   ```

2. Edit `k8s/frontend-deployment.yaml`:
   ```yaml
   image: YOUR_DOCKER_USERNAME/surefinance-frontend:latest
   ```

### Automatic Update (via GitHub Actions):

The GitHub Actions workflow will automatically replace `DOCKER_USERNAME` with your secret value during deployment.

## 🚀 Testing the Pipeline Locally

### Test Docker Builds:

1. **Backend:**
   ```bash
   cd backend
   docker build -t surefinance-backend:test .
   docker run -p 8000:8000 surefinance-backend:test
   ```

2. **Frontend:**
   ```bash
   cd frontend
   docker build -t surefinance-frontend:test .
   docker run -p 80:80 surefinance-frontend:test
   ```

### Test Kubernetes Deployment:

1. Update manifests with your Docker Hub username
2. Apply manifests:
   ```bash
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/backend-service.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   kubectl apply -f k8s/frontend-service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

3. Check status:
   ```bash
   kubectl get deployments
   kubectl get services
   kubectl get pods
   ```

## 🔄 Workflow Overview

The CI/CD pipeline consists of three main jobs:

1. **Backend Job:**
   - Tests Python code
   - Builds Docker image
   - Pushes to Docker Hub
   - Tags with branch name and commit SHA

2. **Frontend Job:**
   - Installs dependencies
   - Builds React application
   - Builds Docker image
   - Pushes to Docker Hub
   - Tags with branch name and commit SHA

3. **Deploy Job:**
   - Updates Kubernetes manifests
   - Applies deployments and services
   - Waits for rollout completion
   - Reports deployment status

## 📊 Pipeline Triggers

The pipeline runs on:
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main` or `master`
- Manual trigger via GitHub Actions UI

## 🐛 Troubleshooting

### Docker Hub Authentication Issues

- Verify `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are correct
- Use an access token instead of password for better security
- Check if Docker Hub rate limits are being hit

### Kubernetes Deployment Issues

- Verify `KUBE_CONFIG` secret is correctly base64 encoded
- Check if kubectl can connect to your cluster:
  ```bash
  kubectl cluster-info
  ```
- Verify image pull secrets if using private registry
- Check pod logs:
  ```bash
  kubectl logs <pod-name>
  ```

### Image Pull Errors

- Verify images are pushed to Docker Hub
- Check image names and tags in deployment manifests
- Ensure Docker Hub repository is public or add image pull secrets

### Build Failures

- Check GitHub Actions logs for specific errors
- Verify all dependencies are listed in `requirements.txt` and `package.json`
- Ensure Dockerfiles are correct

## 🔒 Security Best Practices

1. **Use Access Tokens:** Use Docker Hub access tokens instead of passwords
2. **Restrict Secrets:** Only grant necessary permissions
3. **Private Repositories:** Consider using private Docker Hub repositories
4. **Image Scanning:** Enable Docker Hub vulnerability scanning
5. **Kubernetes RBAC:** Set up proper RBAC for Kubernetes deployments
6. **Secrets Management:** Use Kubernetes secrets for sensitive data

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)

## 🎯 Next Steps

1. Set up GitHub secrets
2. Update Docker Hub username in manifests (or let GitHub Actions handle it)
3. Configure Kubernetes cluster access
4. Push code to trigger the pipeline
5. Monitor deployments in GitHub Actions
6. Access your application via Kubernetes service or ingress

## 💡 Tips

- Start with a local Minikube cluster for testing
- Test Docker builds locally before pushing
- Use feature branches to test pipeline changes
- Monitor Docker Hub for image builds
- Check Kubernetes cluster resources
- Set up monitoring and logging for production deployments


