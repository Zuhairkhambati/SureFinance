# Complete CI/CD Pipeline Setup Guide - Step by Step

This comprehensive guide will walk you through setting up a complete CI/CD pipeline for the SureFinance project from scratch.

## 📚 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: GitHub Repository Setup](#step-1-github-repository-setup)
4. [Step 2: Docker Hub Setup](#step-2-docker-hub-setup)
5. [Step 3: Kubernetes Cluster Setup](#step-3-kubernetes-cluster-setup)
6. [Step 4: GitHub Secrets Configuration](#step-4-github-secrets-configuration)
7. [Step 5: Create GitHub Actions Workflow](#step-5-create-github-actions-workflow)
8. [Step 6: Update Kubernetes Manifests](#step-6-update-kubernetes-manifests)
9. [Step 7: Test the Pipeline Locally](#step-7-test-the-pipeline-locally)
10. [Step 8: Trigger and Monitor Pipeline](#step-8-trigger-and-monitor-pipeline)
11. [Step 9: Verify Deployment](#step-9-verify-deployment)
12. [Troubleshooting](#troubleshooting)
13. [Best Practices](#best-practices)

---

## Overview

This CI/CD pipeline will:
- ✅ Automatically build and test your code on every push
- ✅ Build Docker images for backend and frontend
- ✅ Push images to Docker Hub
- ✅ Deploy to Kubernetes cluster
- ✅ Run health checks and verify deployment

**Pipeline Flow:**
```
Code Push → GitHub Actions → Build & Test → Docker Build → Push to Docker Hub → Deploy to Kubernetes → Verify
```

---

## Prerequisites

Before starting, ensure you have:

### Required Accounts
- [ ] GitHub account with repository access
- [ ] Docker Hub account (free tier is fine)
- [ ] Access to a Kubernetes cluster (local or cloud)

### Required Software
- [ ] Git installed and configured
- [ ] Docker Desktop or Docker Engine installed
- [ ] kubectl installed and configured
- [ ] A code editor (VS Code recommended)

### Knowledge Requirements
- Basic understanding of Git
- Basic understanding of Docker
- Basic understanding of Kubernetes (or willingness to learn)

---

## Step 1: GitHub Repository Setup

### 1.1 Create or Verify Repository

1. **If creating a new repository:**
   - Go to https://github.com/new
   - Name it `SureFinance` (or your preferred name)
   - Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (if you already have code)
   - Click "Create repository"

2. **If using existing repository:**
   - Verify you have push access
   - Ensure your code is committed locally

### 1.2 Initialize Git (if not already done)

```bash
# Navigate to your project directory
cd C:\Users\Zuhair\OneDrive\Desktop\devops\SureFinance

# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit: SureFinance project"
```

### 1.3 Connect to GitHub Repository

```bash
# Add remote (replace YOUR_USERNAME and YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Or if using SSH:
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your code
git branch -M main
git push -u origin main
```

**Verification:**
- Go to your GitHub repository
- Verify all files are present
- Check that you can see your code

---

## Step 2: Docker Hub Setup

### 2.1 Create Docker Hub Account

1. Go to https://hub.docker.com/
2. Click "Sign Up" if you don't have an account
3. Complete the registration process
4. Verify your email address

### 2.2 Create Docker Hub Repositories

1. **Login to Docker Hub:**
   - Go to https://hub.docker.com/
   - Click "Create Repository" or go to https://hub.docker.com/repositories

2. **Create Backend Repository:**
   - Click "Create Repository"
   - Repository name: `surefinance-backend`
   - Visibility: **Public** (or Private if you have a paid plan)
   - Click "Create"

3. **Create Frontend Repository:**
   - Click "Create Repository" again
   - Repository name: `surefinance-frontend`
   - Visibility: **Public** (or Private if you have a paid plan)
   - Click "Create"

### 2.3 Get Docker Hub Credentials

**Option A: Use Password (Simple but less secure)**
- Your Docker Hub username
- Your Docker Hub password

**Option B: Create Access Token (Recommended for security)**
1. Go to Docker Hub → Account Settings → Security
2. Click "New Access Token"
3. Description: "GitHub Actions CI/CD"
4. Permissions: **Read & Write**
5. Click "Generate"
6. **IMPORTANT:** Copy the token immediately (you won't see it again)
7. Save it securely - you'll use this as `DOCKER_PASSWORD`

**Note:** Use the access token as your `DOCKER_PASSWORD` in GitHub secrets.

---

## Step 3: Kubernetes Cluster Setup

You have three options for Kubernetes:

### Option A: Docker Desktop Kubernetes (Easiest for Local Testing)

1. **Install Docker Desktop:**
   - Download from https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Enable Kubernetes:**
   - Open Docker Desktop
   - Go to Settings → Kubernetes
   - Check "Enable Kubernetes"
   - Click "Apply & Restart"
   - Wait for Kubernetes to start (green indicator)

3. **Verify Installation:**
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

4. **Get Kubeconfig:**
   - The kubeconfig is automatically at: `%USERPROFILE%\.kube\config` (Windows)
   - Or: `~/.kube/config` (Linux/Mac)

### Option B: Minikube (Local Development)

1. **Install Minikube:**
   ```bash
   # Windows (using Chocolatey)
   choco install minikube
   
   # Or download from: https://minikube.sigs.k8s.io/docs/start/
   ```

2. **Start Minikube:**
   ```bash
   minikube start
   minikube addons enable ingress
   ```

3. **Get Kubeconfig:**
   ```bash
   minikube ip  # Note the IP address
   # Config is at: %USERPROFILE%\.minikube\profiles\minikube\config
   ```

### Option C: Cloud Kubernetes (Production)

**AWS EKS:**
```bash
# Install AWS CLI and eksctl
# Create cluster
eksctl create cluster --name surefinance-cluster --region us-east-1

# Get kubeconfig
aws eks update-kubeconfig --name surefinance-cluster --region us-east-1
```

**Google GKE:**
```bash
# Install gcloud CLI
# Create cluster
gcloud container clusters create surefinance-cluster --zone us-central1-a

# Get kubeconfig
gcloud container clusters get-credentials surefinance-cluster --zone us-central1-a
```

**Azure AKS:**
```bash
# Install Azure CLI
# Create cluster
az aks create --resource-group myResourceGroup --name surefinance-cluster

# Get kubeconfig
az aks get-credentials --resource-group myResourceGroup --name surefinance-cluster
```

### 3.1 Encode Kubeconfig for GitHub Secrets

**Windows PowerShell:**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.kube\config"))
```

**Windows CMD:**
```cmd
certutil -encode %USERPROFILE%\.kube\config config.txt
# Then open config.txt and copy the content (without BEGIN/END lines)
```

**Linux/Mac:**
```bash
cat ~/.kube/config | base64 -w 0
```

**Save the output** - you'll need it for GitHub secrets.

---

## Step 4: GitHub Secrets Configuration

### 4.1 Navigate to Secrets

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### 4.2 Add DOCKER_USERNAME Secret

1. Click **New repository secret**
2. Name: `DOCKER_USERNAME`
3. Secret: Your Docker Hub username (e.g., `zuhairkh`)
4. Click **Add secret**

### 4.3 Add DOCKER_PASSWORD Secret

1. Click **New repository secret**
2. Name: `DOCKER_PASSWORD`
3. Secret: Your Docker Hub password OR access token (recommended)
4. Click **Add secret**

### 4.4 Add KUBE_CONFIG Secret

1. Click **New repository secret**
2. Name: `KUBE_CONFIG`
3. Secret: Paste the base64-encoded kubeconfig from Step 3.1
4. Click **Add secret**

**Verification:**
- You should see 3 secrets listed:
  - `DOCKER_USERNAME`
  - `DOCKER_PASSWORD`
  - `KUBE_CONFIG`

---

## Step 5: Create GitHub Actions Workflow

### 5.1 Create Workflow Directory

```bash
# Navigate to your project root
cd C:\Users\Zuhair\OneDrive\Desktop\devops\SureFinance

# Create .github/workflows directory
mkdir -p .github\workflows
```

**Windows PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path .github\workflows
```

### 5.2 Create Workflow File

Create a file named `.github/workflows/ci-cd.yml` with the content provided in the next section.

The workflow file will be created automatically when you push the code, or you can create it manually using the file I'll provide.

---

## Step 6: Update Kubernetes Manifests

### 6.1 Update Backend Deployment

The backend deployment file (`k8s/backend-deployment.yaml`) should use a placeholder or your Docker Hub username.

**Option A: Use Placeholder (Recommended)**
- The workflow will automatically replace `DOCKER_USERNAME` with your secret value

**Option B: Hardcode Your Username**
- Replace `zuhairkh` with your Docker Hub username in:
  - `k8s/backend-deployment.yaml` (line 21)
  - `k8s/frontend-deployment.yaml` (line 21)

### 6.2 Verify Image Names

Ensure the image names match your Docker Hub repositories:
- Backend: `YOUR_USERNAME/surefinance-backend:latest`
- Frontend: `YOUR_USERNAME/surefinance-frontend:latest`

---

## Step 7: Test the Pipeline Locally

### 7.1 Test Docker Builds

**Test Backend:**
```bash
cd backend
docker build -t surefinance-backend:test .
docker run -p 8000:8000 surefinance-backend:test
# Test in browser: http://localhost:8000/docs
```

**Test Frontend:**
```bash
cd frontend
docker build -t surefinance-frontend:test .
docker run -p 80:80 surefinance-frontend:test
# Test in browser: http://localhost
```

### 7.2 Test Kubernetes Deployment (Optional)

```bash
# Update manifests with your Docker Hub username first
# Then apply:
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods
kubectl get services
```

---

## Step 8: Trigger and Monitor Pipeline

### 8.1 Push Code to GitHub

```bash
# Add all files
git add .

# Commit changes
git commit -m "Add CI/CD pipeline configuration"

# Push to trigger workflow
git push origin main
```

### 8.2 Monitor Pipeline Execution

1. **Go to GitHub Actions:**
   - Navigate to your repository on GitHub
   - Click the **Actions** tab

2. **View Workflow Run:**
   - You should see a workflow run in progress
   - Click on it to see details

3. **Monitor Jobs:**
   - **Backend Job:** Builds and pushes backend Docker image
   - **Frontend Job:** Builds and pushes frontend Docker image
   - **Deploy Job:** Deploys to Kubernetes

4. **Check Logs:**
   - Click on each job to see detailed logs
   - Look for any errors or warnings

### 8.3 Verify Docker Hub

1. Go to https://hub.docker.com/
2. Check your repositories:
   - `surefinance-backend` should have a new image
   - `surefinance-frontend` should have a new image
3. Verify tags (should include `latest` and commit SHA)

---

## Step 9: Verify Deployment

### 9.1 Check Kubernetes Resources

```bash
# Check deployments
kubectl get deployments

# Check services
kubectl get services

# Check pods
kubectl get pods

# Check pod logs
kubectl logs -l app=surefinance-backend
kubectl logs -l app=surefinance-frontend
```

### 9.2 Access the Application

**Option A: Port Forwarding**
```bash
# Forward frontend
kubectl port-forward service/frontend-service 8080:80

# Forward backend
kubectl port-forward service/backend-service 8000:8000
```

Then access:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Option B: Using Service IP (if using LoadBalancer)**
```bash
# Get service external IP
kubectl get service frontend-service
kubectl get service backend-service
```

**Option C: Using Ingress (if configured)**
```bash
# Get ingress IP
kubectl get ingress

# Access via ingress hostname
```

### 9.3 Test Application Functionality

1. **Test Frontend:**
   - Open frontend URL
   - Verify UI loads correctly
   - Test file upload functionality

2. **Test Backend API:**
   - Open `/docs` endpoint
   - Test API endpoints
   - Verify CORS is working

3. **Test Integration:**
   - Upload a PDF from frontend
   - Verify backend processes it
   - Check response data

---

## Troubleshooting

### Issue: GitHub Actions Workflow Fails

**Check:**
1. GitHub secrets are correctly set
2. Docker Hub credentials are valid
3. Kubernetes config is correctly base64 encoded
4. Workflow file syntax is correct (YAML indentation)

**Common Errors:**
- `Error: Cannot connect to Docker daemon` → Docker service issue
- `Error: unauthorized: authentication required` → Docker Hub credentials wrong
- `Error: Unable to connect to the server` → Kubernetes config wrong

### Issue: Docker Build Fails

**Check:**
1. Dockerfile syntax is correct
2. All dependencies are in requirements.txt/package.json
3. Build context is correct
4. Docker Hub rate limits (if using free tier)

**Solutions:**
```bash
# Test build locally first
docker build -t test-image .

# Check Dockerfile syntax
docker build --no-cache -t test-image .
```

### Issue: Kubernetes Deployment Fails

**Check:**
1. Pod status: `kubectl get pods`
2. Pod logs: `kubectl logs <pod-name>`
3. Events: `kubectl describe pod <pod-name>`
4. Image pull errors: Check if image exists in Docker Hub

**Common Errors:**
- `ImagePullBackOff` → Image doesn't exist or wrong name
- `CrashLoopBackOff` → Application error, check logs
- `Pending` → Insufficient resources

**Solutions:**
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Delete and recreate
kubectl delete -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
```

### Issue: Application Not Accessible

**Check:**
1. Services are created: `kubectl get services`
2. Pods are running: `kubectl get pods`
3. Port forwarding is correct
4. Firewall/network rules

**Solutions:**
```bash
# Check service endpoints
kubectl get endpoints

# Test service connectivity
kubectl exec -it <pod-name> -- curl http://backend-service:8000
```

---

## Best Practices

### Security

1. **Use Access Tokens:**
   - Use Docker Hub access tokens instead of passwords
   - Rotate tokens regularly

2. **Secrets Management:**
   - Never commit secrets to repository
   - Use GitHub Secrets for sensitive data
   - Consider using external secret management (AWS Secrets Manager, HashiCorp Vault)

3. **Image Security:**
   - Scan images for vulnerabilities
   - Use minimal base images
   - Keep dependencies updated

### Performance

1. **Docker Build Optimization:**
   - Use multi-stage builds
   - Leverage Docker layer caching
   - Use .dockerignore files

2. **Kubernetes Resources:**
   - Set appropriate resource limits
   - Use horizontal pod autoscaling
   - Monitor resource usage

### Monitoring

1. **Set Up Logging:**
   - Use centralized logging (ELK, Loki)
   - Structure logs properly
   - Include correlation IDs

2. **Set Up Monitoring:**
   - Use Prometheus + Grafana
   - Set up alerts
   - Monitor application metrics

3. **Health Checks:**
   - Implement proper liveness/readiness probes
   - Monitor application health
   - Set up uptime monitoring

### CI/CD Improvements

1. **Branch Strategy:**
   - Use feature branches
   - Separate staging/production environments
   - Use branch protection rules

2. **Testing:**
   - Add unit tests
   - Add integration tests
   - Add end-to-end tests

3. **Deployment Strategy:**
   - Use blue-green deployments
   - Implement canary releases
   - Add rollback capabilities

---

## Next Steps

After your CI/CD pipeline is working:

1. ✅ **Add Testing:**
   - Unit tests for backend
   - Component tests for frontend
   - Integration tests

2. ✅ **Improve Security:**
   - Add security scanning
   - Implement secret rotation
   - Add vulnerability scanning

3. ✅ **Add Monitoring:**
   - Set up application monitoring
   - Add logging aggregation
   - Create dashboards

4. ✅ **Optimize Pipeline:**
   - Add caching for faster builds
   - Parallelize jobs where possible
   - Add deployment notifications

5. ✅ **Documentation:**
   - Document deployment process
   - Create runbooks
   - Document troubleshooting steps

---

## Summary Checklist

Use this checklist to ensure everything is set up:

- [ ] GitHub repository created and code pushed
- [ ] Docker Hub account created
- [ ] Docker Hub repositories created (backend and frontend)
- [ ] Kubernetes cluster set up and accessible
- [ ] Kubeconfig encoded and ready
- [ ] GitHub secrets configured (DOCKER_USERNAME, DOCKER_PASSWORD, KUBE_CONFIG)
- [ ] GitHub Actions workflow file created
- [ ] Kubernetes manifests updated
- [ ] Local Docker builds tested
- [ ] Code pushed to trigger pipeline
- [ ] Pipeline executed successfully
- [ ] Images pushed to Docker Hub
- [ ] Application deployed to Kubernetes
- [ ] Application accessible and working
- [ ] Health checks passing

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)

---

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review GitHub Actions logs for detailed error messages
3. Check Kubernetes pod logs and events
4. Verify all secrets and configurations
5. Test components individually (Docker builds, Kubernetes deployments)

---

**Congratulations!** 🎉 You now have a complete CI/CD pipeline set up for your SureFinance project!

