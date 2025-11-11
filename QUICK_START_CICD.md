# Quick Start CI/CD Guide

This is a quick reference for setting up and using the CI/CD pipeline.

## 🚀 Quick Setup (5 Minutes)

### 1. Set GitHub Secrets

Go to: Repository → Settings → Secrets and variables → Actions

Add these secrets:
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub password/token
- `KUBE_CONFIG` - Base64 encoded kubeconfig file

### 2. Update Kubernetes Manifests

Replace `DOCKER_USERNAME` in these files:
- `k8s/backend-deployment.yaml`
- `k8s/frontend-deployment.yaml`

Or let GitHub Actions handle it automatically (recommended).

### 3. Push to GitHub

```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

### 4. Monitor Pipeline

Go to: Repository → Actions → CI/CD Pipeline

Watch the workflow run and deploy your application!

## 📋 Pipeline Overview

```
┌─────────────────┐
│   GitHub Push   │
└────────┬────────┘
         │
         ├─── Backend Job ───┐
         │   - Build Docker  │
         │   - Push to Hub   │
         │                   │
         └─── Frontend Job ──┤
             - Build Docker  │
             - Push to Hub   │
                             │
         ┌───────────────────┘
         │
         └─── Deploy Job ────┐
             - Update K8s    │
             - Deploy Apps   │
             - Verify        │
```

## 🔍 Verify Deployment

### Check GitHub Actions
1. Go to Actions tab
2. Click on the latest workflow run
3. Check all jobs are green ✅

### Check Kubernetes
```bash
kubectl get deployments
kubectl get services
kubectl get pods
```

### Access Application
```bash
# Get service IP
kubectl get service frontend-service

# Or use port forwarding
kubectl port-forward service/frontend-service 8080:80
```

## 🐛 Common Issues

### Issue: Docker Hub authentication failed
**Solution:** Check `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets

### Issue: Kubernetes deployment failed
**Solution:** Verify `KUBE_CONFIG` secret is correct and base64 encoded

### Issue: Image pull error
**Solution:** Check if images are pushed to Docker Hub and repository is public

### Issue: Pods not starting
**Solution:** Check pod logs: `kubectl logs <pod-name>`

## 📚 More Information

See `CICD_SETUP_GUIDE.md` for detailed setup instructions.

## 🎯 Next Steps

1. ✅ Set up GitHub secrets
2. ✅ Push code to trigger pipeline
3. ✅ Verify deployment
4. ✅ Access your application
5. 🔄 Set up monitoring and logging
6. 🔒 Configure production settings
7. 📊 Set up alerts and notifications

## 💡 Tips

- Use feature branches to test pipeline changes
- Check GitHub Actions logs for detailed error messages
- Test Docker builds locally before pushing
- Monitor Docker Hub for image builds
- Set up Kubernetes dashboard for better visibility


