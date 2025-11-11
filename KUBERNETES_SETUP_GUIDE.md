# Kubernetes Setup Guide for GitHub Actions

## 🚨 Common Issue: Docker Desktop Local Cluster

If you're seeing this error:
```
dial tcp: lookup kubernetes.docker.internal on 127.0.0.53:53: no such host
```

**This means your kubeconfig is pointing to Docker Desktop's local Kubernetes cluster, which is not accessible from GitHub Actions runners.**

## ✅ Solution: Use a Cloud Kubernetes Cluster

GitHub Actions runners need to connect to a **publicly accessible** Kubernetes cluster. You have several options:

### Option 1: AWS EKS (Elastic Kubernetes Service)

1. **Create an EKS cluster:**
   ```bash
   # Install AWS CLI and eksctl
   eksctl create cluster \
     --name surefinance-cluster \
     --region us-east-1 \
     --node-type t3.medium \
     --nodes 2
   ```

2. **Get the kubeconfig:**
   ```bash
   aws eks update-kubeconfig --name surefinance-cluster --region us-east-1
   ```

3. **Encode the kubeconfig for GitHub:**
   ```bash
   # Linux/Mac
   cat ~/.kube/config | base64 -w 0
   
   # Windows PowerShell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.kube\config"))
   ```

4. **Add to GitHub Secrets:**
   - Go to: Repository → Settings → Secrets and variables → Actions
   - Add secret: `KUBE_CONFIG` with the base64 encoded value

### Option 2: Google GKE (Google Kubernetes Engine)

1. **Create a GKE cluster:**
   ```bash
   # Install gcloud CLI
   gcloud container clusters create surefinance-cluster \
     --zone us-central1-a \
     --num-nodes 2 \
     --machine-type e2-medium
   ```

2. **Get the kubeconfig:**
   ```bash
   gcloud container clusters get-credentials surefinance-cluster \
     --zone us-central1-a
   ```

3. **Encode and add to GitHub Secrets** (same as Option 1, step 3-4)

### Option 3: Azure AKS (Azure Kubernetes Service)

1. **Create an AKS cluster:**
   ```bash
   # Install Azure CLI
   az aks create \
     --resource-group myResourceGroup \
     --name surefinance-cluster \
     --node-count 2 \
     --node-vm-size Standard_B2s
   ```

2. **Get the kubeconfig:**
   ```bash
   az aks get-credentials \
     --resource-group myResourceGroup \
     --name surefinance-cluster
   ```

3. **Encode and add to GitHub Secrets** (same as Option 1, step 3-4)

### Option 4: DigitalOcean Kubernetes

1. **Create a cluster via UI or CLI:**
   ```bash
   doctl kubernetes cluster create surefinance-cluster \
     --region nyc1 \
     --size s-2vcpu-4gb \
     --count 2
   ```

2. **Get the kubeconfig:**
   ```bash
   doctl kubernetes cluster kubeconfig save surefinance-cluster
   ```

3. **Encode and add to GitHub Secrets** (same as Option 1, step 3-4)

### Option 5: Self-Hosted Runner (Advanced)

If you want to use your local Docker Desktop cluster, you can set up a self-hosted GitHub Actions runner:

1. **Set up a self-hosted runner** on a machine that has access to your Docker Desktop cluster
2. **Update the workflow** to use `runs-on: self-hosted` instead of `runs-on: ubuntu-latest`

⚠️ **Note:** Self-hosted runners require your machine to be always on and accessible.

## 🔍 How to Verify Your Kubeconfig

Before encoding your kubeconfig, verify it points to an accessible cluster:

```bash
# Check the server endpoint
kubectl config view --minify | grep server

# Test connection
kubectl cluster-info
kubectl get nodes
```

**Good endpoints (will work in GitHub Actions):**
- `https://xxx.yl4.us-east-1.eks.amazonaws.com` (AWS EKS)
- `https://xxx.xxx.xxx.xxx` (Public IP)
- `https://xxx.gke.googleapis.com` (GKE)

**Bad endpoints (won't work in GitHub Actions):**
- `https://kubernetes.docker.internal:6443` (Docker Desktop)
- `https://127.0.0.1:6443` (Localhost)
- `https://localhost:6443` (Localhost)

## 📝 Step-by-Step: Update Your GitHub Secret

1. **Get a valid kubeconfig** from one of the cloud providers above

2. **Encode it:**
   
   **Windows PowerShell:**
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.kube\config"))
   ```
   
   **Linux/Mac:**
   ```bash
   cat ~/.kube/config | base64 -w 0
   ```

3. **Update GitHub Secret:**
   - Go to your repository on GitHub
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Find `KUBE_CONFIG` secret
   - Click **Update**
   - Paste the base64 encoded kubeconfig
   - Click **Update secret**

4. **Test the pipeline:**
   - Push a commit or manually trigger the workflow
   - Check the "Verify cluster connection" step in the Actions tab

## 🛠️ Troubleshooting

### Issue: "Kubeconfig contains 'kubernetes.docker.internal'"

**Solution:** You're using a Docker Desktop kubeconfig. Follow one of the cloud provider options above.

### Issue: "Failed to connect to cluster"

**Possible causes:**
1. Cluster endpoint is not publicly accessible
2. Firewall blocking GitHub Actions IPs
3. Invalid or expired credentials in kubeconfig
4. Network policies blocking access

**Solutions:**
- Verify cluster endpoint is accessible: `curl -k <cluster-endpoint>/healthz`
- Check cluster firewall rules allow GitHub Actions IP ranges
- Regenerate kubeconfig with fresh credentials
- For EKS: Ensure cluster has public endpoint enabled

### Issue: "Failed to get nodes"

**Possible causes:**
1. RBAC permissions insufficient
2. Service account lacks permissions
3. Cluster authentication failed

**Solutions:**
- Verify your kubeconfig user has cluster-admin or appropriate permissions
- Check RBAC rules: `kubectl auth can-i get nodes --all-namespaces`
- Regenerate kubeconfig with proper permissions

## 💰 Cost Considerations

**Free/Cheap Options:**
- **Minikube on Cloud VM:** ~$5-10/month (requires self-hosted runner)
- **DigitalOcean:** ~$24/month (2 nodes)
- **AWS EKS:** ~$72/month + EC2 costs
- **GKE:** ~$72/month + node costs (free tier available)
- **AKS:** ~$73/month + node costs

**Recommendation for Development:**
- Use DigitalOcean or a small GKE cluster for cost-effective testing
- Use managed services (EKS/GKE/AKS) for production

## 🔐 Security Best Practices

1. **Use least privilege:** Don't use cluster-admin unless necessary
2. **Rotate credentials:** Regularly update kubeconfig credentials
3. **Use service accounts:** Create dedicated service accounts for CI/CD
4. **Enable audit logging:** Monitor cluster access
5. **Use secrets management:** Consider using external secret managers

## 📚 Additional Resources

- [AWS EKS Getting Started](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html)
- [GKE Quickstart](https://cloud.google.com/kubernetes-engine/docs/quickstart)
- [AKS Quickstart](https://docs.microsoft.com/azure/aks/kubernetes-walkthrough)
- [GitHub Actions Self-Hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)

