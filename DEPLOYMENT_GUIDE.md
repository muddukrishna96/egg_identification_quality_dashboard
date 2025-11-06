# AWS EC2 Deployment Guide
## Egg Tray Quality Inspection Dashboard

Complete guide to deploy the dashboard on AWS EC2 using free tier.

---

## 📋 Prerequisites

- ✅ AWS Account (free tier eligible)
- ✅ GitHub repository with model uploaded to Releases (v1.0.0)
- ✅ SSH client (Windows/Mac/Linux)
- ✅ Basic terminal knowledge

---

## 🚀 Quick Deployment (30 minutes)

### Step 1: Create EC2 Instance

### Step 1: Create EC2 Instance

**Go to AWS Console → EC2 → Launch Instance**

#### 1.1 Basic Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| **Name** | `egg-dashboard` | Any name you prefer |
| **AMI** | Ubuntu Server 22.04 LTS | Free tier eligible |
| **Instance type** | t2.small | 2GB RAM (Recommended) |
| **Storage** | 30 GB gp3 | Free tier: up to 30GB |

**⚠️ Important**: 
- t2.micro (1GB RAM) will run out of memory with YOLO model
- Use t2.small (~$17/month) OR add 2GB swap space to t2.micro

#### 1.2 Create Key Pair

1. Click **"Create new key pair"**
2. **Name**: `egg-dashboard-key`
3. **Type**: RSA
4. **Format**: `.pem` (for SSH)
5. **Download and save securely** - You can't download it again!

#### 1.3 Network Settings (Security Group)

Create security group: `egg-dashboard-sg` with these inbound rules:

| Type | Port | Source | Description |
|------|------|--------|-------------|
| SSH | 22 | My IP | SSH access (restrict to your IP) |
| HTTP | 80 | 0.0.0.0/0 | Web access |
| HTTPS | 443 | 0.0.0.0/0 | Secure web (optional) |
| Custom TCP | 8501 | 0.0.0.0/0 | Streamlit direct access |

#### 1.4 Launch

- Click **"Launch Instance"**
- Wait until status shows **"Running"** (green)
- **Copy Public IPv4 address** (e.g., `54.123.45.67`)

---

### Step 2: Verify Model in GitHub Releases

Ensure your model is uploaded:

1. Go to: `https://github.com/YOUR_USERNAME/egg_identification_quality_dashboard/releases`
2. Check for release: **v1.0.0**
3. Verify `best.pt` file is attached

**Model URL should be:**
```
https://github.com/YOUR_USERNAME/egg_identification_quality_dashboard/releases/download/v1.0.0/best.pt
```

---

### Step 3: Connect to EC2

#### On Windows (PowerShell):

```powershell
# Navigate to where your key is saved
cd ~\Downloads

# Set proper permissions
icacls.exe egg-dashboard-key.pem /reset
icacls.exe egg-dashboard-key.pem /grant:r "$($env:USERNAME):(R)"
icacls.exe egg-dashboard-key.pem /inheritance:r

# Connect (replace with YOUR IP)
ssh -i egg-dashboard-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

#### On Mac/Linux:

```bash
# Set proper permissions
chmod 400 egg-dashboard-key.pem

# Connect (replace with YOUR IP)  
ssh -i egg-dashboard-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

### Step 4: Deploy Application

Once connected to EC2, run:

```bash
# Download deployment script
wget https://raw.githubusercontent.com/muddukrishna96/egg_identification_quality_dashboard/aws_deployment/deploy.sh

# Make executable
chmod +x deploy.sh

# Run deployment (takes 10-15 minutes)
./deploy.sh
```

**What this does:**
- ✅ Updates system packages
- ✅ Installs Python 3.10 and dependencies
- ✅ Clones your repository
- ✅ Downloads model from GitHub Releases
- ✅ Creates systemd services (auto-restart)
- ✅ Configures Nginx reverse proxy
- ✅ Sets up firewall

**Deployment output:**
```
🚀 Starting deployment...
📦 Updating system...
🐍 Installing Python 3.10...
📸 Installing OpenCV dependencies...
📥 Cloning repository...
🔧 Setting up virtual environment...
📚 Installing Python packages...
🤖 Downloading model from GitHub Releases...
✅ Model downloaded successfully
⚙️  Setting up systemd services...
🎬 Starting services...
🌐 Installing Nginx...
✅ Deployment Complete!
```

---

### Step 5: Add Swap Space (If using t2.micro)

**Only needed if you're using t2.micro (1GB RAM)**

Open a **new SSH session** (keep the deployment running) and run:

```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
free -h

# Restart backend
sudo systemctl restart egg-backend
```

---

### Step 6: Access Your Dashboard

#### Open in browser:

```
http://YOUR_EC2_PUBLIC_IP
```

**Example**: If your IP is `54.123.45.67`:
```
http://54.123.45.67
```

#### API Documentation:

```
http://YOUR_EC2_PUBLIC_IP/api/docs
```

#### Test the Dashboard:

1. Upload an egg tray image or select a sample
2. Click **"🔍 Predict"**
3. View detection results with metrics
4. First prediction may take 15-30 seconds (model loading)

---

## 🔧 Management Commands

### Check Service Status

```bash
# Check both services
sudo systemctl status egg-backend egg-frontend

# Check individual services
sudo systemctl status egg-backend
sudo systemctl status egg-frontend
sudo systemctl status nginx
```

### View Logs

```bash
# Real-time backend logs
sudo journalctl -u egg-backend -f

# Real-time frontend logs
sudo journalctl -u egg-frontend -f

# Last 50 lines
sudo journalctl -u egg-backend -n 50
```

### Restart Services

```bash
# Restart both
sudo systemctl restart egg-backend egg-frontend

# Restart individual
sudo systemctl restart egg-backend
sudo systemctl restart egg-frontend
sudo systemctl restart nginx
```

### Update Application

```bash
cd /home/ubuntu/egg_identification_quality_dashboard
git pull origin aws_deployment
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart egg-backend egg-frontend
```

---

## 🛠️ Troubleshooting

### Issue 1: Backend Crashes (Killed)

**Symptom**: Service shows `code=killed, status=9/KILL`

**Cause**: Out of memory (OOM killer)

**Solution**: Add swap space (see Step 5)

```bash
sudo journalctl -u egg-backend -n 50
# Look for "killed" or "status=9"
```

### Issue 2: Can't SSH to EC2

**Solutions**:
- Check security group allows SSH (port 22) from your IP
- Verify instance is "Running"
- Check you're using correct key file
- Try verbose: `ssh -v -i key.pem ubuntu@IP`

### Issue 3: Services Not Starting

```bash
# Check logs for errors
sudo journalctl -u egg-backend -n 50
sudo journalctl -u egg-frontend -n 50

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart egg-backend egg-frontend
```

### Issue 4: Port Conflicts

```bash
# Find process using port
sudo lsof -i :8000
sudo lsof -i :8501

# Kill process (replace PID)
sudo kill -9 PID

# Restart service
sudo systemctl restart egg-backend
```

### Issue 5: Nginx Shows Default Page

```bash
# Reconfigure Nginx
sudo tee /etc/nginx/sites-available/egg-dashboard > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
    }
}
EOF

# Enable and restart
sudo ln -sf /etc/nginx/sites-available/egg-dashboard /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Issue 6: Model Download Fails

```bash
# Manual download
cd /home/ubuntu/egg_identification_quality_dashboard
mkdir -p model
wget -O model/best.pt https://github.com/YOUR_USERNAME/egg_identification_quality_dashboard/releases/download/v1.0.0/best.pt

# Restart backend
sudo systemctl restart egg-backend
```

---

## 💰 Cost Breakdown

### Free Tier (First 12 Months)

| Resource | Free Tier | After Free Tier |
|----------|-----------|-----------------|
| EC2 t2.micro | 750 hrs/month | ~$8-10/month |
| EC2 t2.small | Not free | ~$17/month |
| EBS Storage (30GB) | 30 GB free | ~$3/month |
| Data Transfer | 15 GB/month | $0.09/GB |

### Recommendations:

**Option 1: Free Tier (t2.micro + swap)**
- Cost: $0 for 12 months, then ~$11/month
- Performance: Slower (15-30s predictions)
- Best for: Testing, low usage

**Option 2: t2.small (Recommended)**
- Cost: ~$17/month (no free tier)
- Performance: Fast (3-5s predictions)
- Best for: Production, regular usage

**Cost Optimization:**
- Stop instance when not in use (doesn't count toward hours)
- Use only 1 Elastic IP
- Set up billing alerts in AWS

---

## 🔒 Security Best Practices

### 1. Restrict SSH Access

After deployment:

1. Go to EC2 → Security Groups → `egg-dashboard-sg`
2. Edit inbound rules
3. SSH rule: Change source from "Anywhere" to "My IP"

### 2. Regular Updates

```bash
# Monthly system updates
sudo apt-get update && sudo apt-get upgrade -y

# Reboot if kernel updated
sudo reboot
```

### 3. Enable HTTPS (Optional)

If you have a domain name:

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renew
sudo systemctl enable certbot.timer
```

### 4. Backup Data

```bash
# Backup model
cp /home/ubuntu/egg_identification_quality_dashboard/model/best.pt ~/

# Create EC2 snapshot
# AWS Console → EC2 → Volumes → Select volume → Create snapshot
```

---

## 🔄 Auto-Deploy Setup (Optional)

Enable automatic deployment when you push code to GitHub.

### ⚠️ Important Note

The repository includes a **generic GitHub Actions workflow** file (`.github/workflows/deploy.yml`) that is **NOT configured by default**. You must set up GitHub Secrets to make it work.

### Step 1: Verify Workflow File Exists

The file `.github/workflows/deploy.yml` should already be in the repository. If not, it will be created when you clone the `aws_deployment` branch.

### Step 2: Setup GitHub Secrets

**This is REQUIRED to activate auto-deployment:**

1. **Go to your GitHub repository**
   - Navigate to: `https://github.com/YOUR_USERNAME/egg_identification_quality_dashboard`

2. **Open Settings**
   - Click **Settings** tab (top right)
   - Click **Secrets and variables** → **Actions** (left sidebar)

3. **Add First Secret: EC2_SSH_KEY**
   - Click **"New repository secret"**
   - **Name**: `EC2_SSH_KEY`
   - **Value**: Paste the **entire content** of your `.pem` key file
   
   ```bash
   # On Windows PowerShell (to view key content)
   Get-Content egg-dashboard-key.pem | clip  # Copies to clipboard
   
   # On Mac/Linux
   cat egg-dashboard-key.pem  # Copy the output
   ```
   
   - Click **"Add secret"**

4. **Add Second Secret: EC2_HOST**
   - Click **"New repository secret"** again
   - **Name**: `EC2_HOST`
   - **Value**: Your EC2 public IP address (e.g., `54.1.45.67`)
   - Click **"Add secret"**

### Step 3: How It Works

Once secrets are configured, the workflow will **automatically**:

1. **Trigger** on every push to `aws_deployment` branch
2. **SSH** into your EC2 instance
3. **Pull** latest code from GitHub
4. **Update** Python dependencies
5. **Restart** backend and frontend services
6. **Verify** deployment success

### Step 4: Test Auto-Deploy

```bash
# Make a small change locally
echo "# Test auto-deploy" >> README.md

# Commit and push
git add README.md
git commit -m "Test auto-deploy"
git push origin aws_deployment
```

**Check deployment:**
1. Go to GitHub → Actions tab
2. You'll see the workflow running
3. Takes ~2-3 minutes to complete

### Step 5: Manual Trigger (Alternative)

You can also trigger deployment manually without pushing code:

1. Go to GitHub → **Actions** tab
2. Click **"Deploy to AWS EC2"** workflow
3. Click **"Run workflow"** button
4. Select branch: `aws_deployment`
5. Click **"Run workflow"**

### Workflow Status

**✅ Active** - If you see green checkmarks in Actions tab  
**❌ Failed** - Click on the failed run to see error logs  
**⚠️ Inactive** - If secrets are not configured

### Troubleshooting Auto-Deploy

**Issue: Workflow fails with "Permission denied"**
- Check `EC2_SSH_KEY` secret contains the complete .pem file
- Ensure key includes `-----BEGIN RSA PRIVATE KEY-----` header

**Issue: "Host key verification failed"**
- Workflow includes `StrictHostKeyChecking=no` - should not happen
- Check `EC2_HOST` secret has correct IP address

**Issue: "Connection timeout"**
- Verify EC2 security group allows SSH (port 22) from GitHub IPs
- Or allow from anywhere (0.0.0.0/0) for GitHub Actions

**Issue: Services don't restart**
- SSH to EC2 and run: `sudo visudo`
- Add: `ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart egg-backend, /bin/systemctl restart egg-frontend`

### Disable Auto-Deploy

If you don't want auto-deployment:

```bash
# Delete the workflow file
rm -rf .github/workflows/deploy.yml

# Commit and push
git add .
git commit -m "Disable auto-deploy"
git push origin aws_deployment
```

---

## 📊 Monitoring

### CloudWatch (AWS Built-in)

1. EC2 Console → Your instance → Monitoring
2. Enable detailed monitoring
3. Set up alarms for CPU, memory, disk

### Service Health Check

```bash
# Quick health check script
#!/bin/bash
echo "=== Service Status ==="
sudo systemctl is-active egg-backend egg-frontend nginx

echo -e "\n=== Memory Usage ==="
free -h

echo -e "\n=== Disk Usage ==="
df -h /

echo -e "\n=== Last 5 Backend Logs ==="
sudo journalctl -u egg-backend -n 5 --no-pager
```

---

## ✅ Post-Deployment Checklist

- [ ] EC2 instance running
- [ ] SSH access working
- [ ] Deployment script completed successfully
- [ ] Backend service active: `sudo systemctl status egg-backend`
- [ ] Frontend service active: `sudo systemctl status egg-frontend`
- [ ] Nginx running: `sudo systemctl status nginx`
- [ ] Dashboard accessible in browser
- [ ] Test image upload and prediction works
- [ ] API docs accessible at `/api/docs`
- [ ] Swap space added (if using t2.micro)
- [ ] Security group SSH restricted to your IP
- [ ] Billing alerts configured
- [ ] Backup plan in place

---

## 📞 Quick Reference

### Important URLs

```
Dashboard: http://YOUR_EC2_IP
API Docs:  http://YOUR_EC2_IP/api/docs
Direct:    http://YOUR_EC2_IP:8501
```

### Important Paths

```
App:    /home/ubuntu/egg_identification_quality_dashboard
Venv:   /home/ubuntu/egg_identification_quality_dashboard/venv
Model:  /home/ubuntu/egg_identification_quality_dashboard/model/best.pt
Logs:   journalctl -u egg-backend / egg-frontend
```

### Essential Commands

```bash
# Status
sudo systemctl status egg-backend egg-frontend

# Logs
sudo journalctl -u egg-backend -f

# Restart
sudo systemctl restart egg-backend egg-frontend

# Update
cd /home/ubuntu/egg_identification_quality_dashboard && git pull

# Health
free -h && df -h && sudo systemctl is-active egg-backend
```

---

## 🎉 Success!

Your Egg Tray Quality Inspection Dashboard is now live!

**Share URL:** `http://YOUR_EC2_IP`

**Estimated Time:** 30-45 minutes  
**Monthly Cost:** $0 (free tier) or ~$17 (t2.small)

For support, check the troubleshooting section or review service logs.
