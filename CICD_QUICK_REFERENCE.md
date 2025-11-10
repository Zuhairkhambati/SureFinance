# CI/CD Quick Reference Card

## 🚀 Quick Setup (5 Steps)

### 1. Docker Hub Setup
```bash
# Create repositories:
# - surefinance-backend
# - surefinance-frontend
```

### 2. GitHub Secrets
```
Repository → Settings → Secrets → Actions
- DOCKER_USERNAME: your_dockerhub_username
- DOCKER_PASSWORD: your_token_or_password
- KUBE_CONFIG: base64_encoded_kubeconfig
```

### 3. Encode Kubeconfig
**Windows PowerShell:**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.kube\config"))
```

**Linux/Mac:**
```bash
cat ~/.kube/config | base64 -w 0
```

### 4. Push Code
```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

### 5. Monitor
```
GitHub → Actions → CI/CD Pipeline
```

---

## 📋 Pipeline Jobs

| Job | Description | Duration |
|-----|-------------|----------|
| **Backend** | Build & push backend image | ~3-5 min |
| **Frontend** | Build & push frontend image | ~3-5 min |
| **Deploy** | Deploy to Kubernetes | ~2-3 min |

---

## 🔍 Verification Commands

### Check Pipeline
```bash
# GitHub Actions
gh run list  # If GitHub CLI installed
```

### Check Docker Hub
```bash
# Visit: https://hub.docker.com/r/YOUR_USERNAME/surefinance-backend
# Visit: https://hub.docker.com/r/YOUR_USERNAME/surefinance-frontend
```

### Check Kubernetes
```bash
kubectl get deployments
kubectl get services
kubectl get pods
kubectl logs -l app=surefinance-backend
kubectl logs -l app=surefinance-frontend
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Docker auth failed | Check DOCKER_USERNAME/PASSWORD secrets |
| K8s connection failed | Verify KUBE_CONFIG is base64 encoded |
| Image pull error | Check image exists in Docker Hub |
| Pod crash | Check logs: `kubectl logs <pod-name>` |

---

## 📝 Workflow Triggers

- ✅ Push to `main`, `master`, `develop`
- ✅ Pull requests to `main`/`master`
- ✅ Manual trigger (workflow_dispatch)

---

## 🔗 Useful Links

- **Full Guide:** `COMPLETE_CICD_GUIDE.md`
- **Setup Guide:** `CICD_SETUP_GUIDE.md`
- **Checklist:** `CICD_CHECKLIST.md`
- **Workflow File:** `.github/workflows/ci-cd.yml`

---

## ⚡ Quick Commands

### Local Testing
```bash
# Test backend build
cd backend && docker build -t test-backend .

# Test frontend build
cd frontend && docker build -t test-frontend .
```

### Kubernetes Access
```bash
# Port forward
kubectl port-forward service/frontend-service 8080:80
kubectl port-forward service/backend-service 8000:8000

# Access:
# Frontend: http://localhost:8080
# Backend: http://localhost:8000/docs
```

---

## 📊 Pipeline Status

Check status at: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`

---

**Need help?** See `COMPLETE_CICD_GUIDE.md` for detailed instructions.

