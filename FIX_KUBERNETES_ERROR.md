# Quick Fix: Kubernetes Connection Error in GitHub Actions

## 🚨 The Problem

You're seeing this error:
```
dial tcp: lookup kubernetes.docker.internal on 127.0.0.53:53: no such host
```

**Root Cause:** Your `KUBE_CONFIG` GitHub secret contains a kubeconfig pointing to Docker Desktop's local Kubernetes cluster (`kubernetes.docker.internal:6443`), which is not accessible from GitHub Actions cloud runners.

## ✅ Quick Solution (3 Steps)

### Step 1: Get a Cloud Kubernetes Cluster

Choose one:
- **AWS EKS** (recommended for AWS users)
- **Google GKE** (recommended for GCP users)  
- **Azure AKS** (recommended for Azure users)
- **DigitalOcean** (cheapest option ~$24/month)

See `KUBERNETES_SETUP_GUIDE.md` for detailed setup instructions.

### Step 2: Get the Correct Kubeconfig

After creating your cloud cluster, get the kubeconfig:

**AWS EKS:**
```bash
aws eks update-kubeconfig --name your-cluster-name --region us-east-1
```

**Google GKE:**
```bash
gcloud container clusters get-credentials your-cluster-name --zone us-central1-a
```

**Azure AKS:**
```bash
az aks get-credentials --resource-group myResourceGroup --name your-cluster-name
```

### Step 3: Update GitHub Secret

1. **Encode your new kubeconfig:**

   **Windows PowerShell:**
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.kube\config"))
   ```

   **Linux/Mac:**
   ```bash
   cat ~/.kube/config | base64 -w 0
   ```

2. **Update the secret:**
   - Go to: GitHub Repository → Settings → Secrets and variables → Actions
   - Find `KUBE_CONFIG` secret
   - Click **Update**
   - Paste the new base64 encoded kubeconfig
   - Click **Update secret**

3. **Test:**
   - Push a commit or manually trigger the workflow
   - The error should be resolved!

## 🔍 Verify Your Kubeconfig Before Encoding

Make sure your kubeconfig points to a cloud cluster:

```bash
kubectl config view --minify | grep server
```

**✅ Good (will work):**
- `https://xxx.yl4.us-east-1.eks.amazonaws.com`
- `https://xxx.gke.googleapis.com`
- `https://xxx.xxx.xxx.xxx` (public IP)

**❌ Bad (won't work):**
- `https://kubernetes.docker.internal:6443`
- `https://127.0.0.1:6443`
- `https://localhost:6443`

## 📋 What Changed in the Workflow

The workflow now:
1. ✅ Detects Docker Desktop kubeconfigs early
2. ✅ Provides clear error messages
3. ✅ Shows helpful troubleshooting steps
4. ✅ Validates kubeconfig before attempting connection

## 💡 Alternative: Self-Hosted Runner

If you want to keep using Docker Desktop, you can set up a self-hosted GitHub Actions runner on your local machine. However, this requires:
- Your machine to be always on
- Network accessibility
- More maintenance

See GitHub docs: [Self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners)

## 📚 More Help

- See `KUBERNETES_SETUP_GUIDE.md` for detailed cloud provider setup
- Check workflow logs in GitHub Actions for specific error messages
- The workflow now provides helpful error messages if issues persist

