# CI/CD Setup Checklist

Use this checklist to ensure everything is set up correctly for your CI/CD pipeline.

## 📋 Pre-Setup Checklist

### GitHub Repository
- [ ] Repository is created on GitHub
- [ ] Code is pushed to repository
- [ ] Repository has appropriate permissions

### Docker Hub
- [ ] Docker Hub account created
- [ ] Docker Hub repositories created:
  - [ ] `surefinance-backend`
  - [ ] `surefinance-frontend`
- [ ] Docker Hub username noted
- [ ] Docker Hub access token created (recommended) or password ready

### Kubernetes Cluster
- [ ] Kubernetes cluster is running
- [ ] `kubectl` is installed
- [ ] `kubectl` is configured to access cluster
- [ ] Cluster has sufficient resources
- [ ] Ingress controller installed (optional, for ingress)
- [ ] Kubernetes config file located

## 🔐 GitHub Secrets Setup

Go to: Repository → Settings → Secrets and variables → Actions

### Required Secrets
- [ ] `DOCKER_USERNAME` - Docker Hub username
- [ ] `DOCKER_PASSWORD` - Docker Hub password or access token
- [ ] `KUBE_CONFIG` - Base64 encoded Kubernetes config file

### How to Get KUBE_CONFIG

**Linux/Mac:**
```bash
cat ~/.kube/config | base64 -w 0
```

**Windows PowerShell:**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.kube\config"))
```

**Windows CMD:**
```cmd
certutil -encode %USERPROFILE%\.kube\config config.txt
# Then copy the content (without -----BEGIN CERTIFICATE----- and -----END CERTIFICATE-----)
```

## 📁 File Checklist

### Docker Files
- [ ] `backend/Dockerfile` exists
- [ ] `frontend/Dockerfile` exists
- [ ] `frontend/nginx.conf` exists
- [ ] `backend/.dockerignore` exists
- [ ] `frontend/.dockerignore` exists

### Kubernetes Files
- [ ] `k8s/backend-deployment.yaml` exists
- [ ] `k8s/backend-service.yaml` exists
- [ ] `k8s/frontend-deployment.yaml` exists
- [ ] `k8s/frontend-service.yaml` exists
- [ ] `k8s/ingress.yaml` exists

### GitHub Actions
- [ ] `.github/workflows/ci-cd.yml` exists

### Documentation
- [ ] `CICD_SETUP_GUIDE.md` exists
- [ ] `QUICK_START_CICD.md` exists
- [ ] `CICD_SUMMARY.md` exists
- [ ] `CICD_CHECKLIST.md` exists (this file)

## 🔧 Configuration Checklist

### Kubernetes Manifests
- [ ] `DOCKER_USERNAME` placeholder in `k8s/backend-deployment.yaml`
- [ ] `DOCKER_USERNAME` placeholder in `k8s/frontend-deployment.yaml`
- [ ] Image tags set to `:latest` (or specific version)
- [ ] Resource limits are appropriate
- [ ] Replica counts are set

### Backend Configuration
- [ ] CORS settings updated in `backend/main.py`
- [ ] Port is set to 8000
- [ ] Dependencies are in `requirements.txt`

### Frontend Configuration
- [ ] Build command is `npm run build`
- [ ] Nginx configuration is correct
- [ ] API proxy settings are configured
- [ ] Dependencies are in `package.json`

## 🧪 Testing Checklist

### Local Docker Builds
- [ ] Backend Docker image builds successfully
- [ ] Frontend Docker image builds successfully
- [ ] Backend container runs locally
- [ ] Frontend container runs locally
- [ ] Containers can communicate

### Kubernetes Deployment
- [ ] Can connect to Kubernetes cluster
- [ ] Kubernetes manifests are valid
- [ ] Can apply manifests manually
- [ ] Pods start successfully
- [ ] Services are created
- [ ] Can access frontend service
- [ ] Can access backend service
- [ ] Frontend can communicate with backend

## 🚀 Pipeline Execution Checklist

### First Run
- [ ] Code is pushed to GitHub
- [ ] GitHub Actions workflow is triggered
- [ ] Backend job completes successfully
- [ ] Frontend job completes successfully
- [ ] Deploy job completes successfully
- [ ] Images are pushed to Docker Hub
- [ ] Kubernetes deployment is successful
- [ ] Application is accessible

### Verification
- [ ] Check GitHub Actions logs
- [ ] Verify images in Docker Hub
- [ ] Check Kubernetes pods status
- [ ] Check Kubernetes services
- [ ] Test application functionality
- [ ] Verify health checks
- [ ] Check logs for errors

## 🔍 Post-Deployment Checklist

### Application Access
- [ ] Frontend is accessible
- [ ] Backend API is accessible
- [ ] API endpoints are working
- [ ] Frontend can communicate with backend
- [ ] No CORS errors
- [ ] Health checks are passing

### Monitoring
- [ ] Pods are running
- [ ] Services are healthy
- [ ] No errors in logs
- [ ] Resource usage is normal
- [ ] Application is responsive

## 🐛 Troubleshooting Checklist

If something goes wrong:

- [ ] Check GitHub Actions logs
- [ ] Verify GitHub secrets are correct
- [ ] Check Docker Hub for images
- [ ] Verify Kubernetes config is correct
- [ ] Check pod logs: `kubectl logs <pod-name>`
- [ ] Check service endpoints: `kubectl get endpoints`
- [ ] Verify network connectivity
- [ ] Check resource limits
- [ ] Verify image pull secrets (if using private repo)
- [ ] Check ingress configuration (if using ingress)

## 📊 Maintenance Checklist

### Regular Checks
- [ ] Monitor GitHub Actions runs
- [ ] Check Docker Hub for new images
- [ ] Monitor Kubernetes cluster health
- [ ] Review application logs
- [ ] Check resource usage
- [ ] Update dependencies
- [ ] Review security updates
- [ ] Backup configurations

### Updates
- [ ] Update Docker images
- [ ] Update Kubernetes manifests
- [ ] Update GitHub Actions workflow
- [ ] Update documentation
- [ ] Test updates in staging
- [ ] Deploy updates to production

## ✅ Completion

Once all items are checked:
- [ ] All secrets are configured
- [ ] All files are in place
- [ ] Local testing is successful
- [ ] Pipeline runs successfully
- [ ] Application is deployed
- [ ] Application is accessible
- [ ] Documentation is reviewed

## 🎉 Success!

Your CI/CD pipeline is ready! 🚀

## 📚 Resources

- **Setup Guide:** `CICD_SETUP_GUIDE.md`
- **Quick Start:** `QUICK_START_CICD.md`
- **Summary:** `CICD_SUMMARY.md`
- **Kubernetes:** `k8s/README.md`

## 💡 Tips

- Test locally before pushing to GitHub
- Use feature branches for testing
- Monitor GitHub Actions for errors
- Keep Docker Hub credentials secure
- Regularly update dependencies
- Monitor resource usage
- Set up alerts for failures
- Review logs regularly
- Keep documentation updated


