# AWS EC2 Deployment Guide
# Egg Tray Quality Inspection Dashboard

## 📋 Prerequisites

1. **AWS Account** with free tier access
2. **GitHub Account** with your repository
3. **SSH Key** for EC2 access
4. **Model File** uploaded to GitHub Releases

---

## 🚀 Quick Start Deployment

### Step 1: Create EC2 Instance

1. **Log in to AWS Console**
   - Go to: https://console.aws.amazon.com/ec2/

2. **Launch Instance**
   - Click "Launch Instance"
   - Name: `egg-tray-dashboard`

3. **Choose AMI**
   - Select: **Ubuntu Server 22.04 LTS (Free tier eligible)**
   - Architecture: 64-bit (x86)

4. **Choose Instance Type**
   - Select: **t2.micro** (Free tier: 750 hours/month)
   - 1 vCPU, 1 GB RAM

5. **Create/Select Key Pair**
   - Create new key pair or use existing
   - Name: `egg-dashboard-key`
   - Type: RSA
   - Format: .pem (for SSH) or .ppk (for PuTTY)
   - **Download and save securely**

6. **Configure Network Settings**
   - Create security group: `egg-dashboard-sg`
   - Allow:
     - ✅ SSH (Port 22) - Your IP
     - ✅ HTTP (Port 80) - Anywhere (0.0.0.0/0)
     - ✅ HTTPS (Port 443) - Anywhere (0.0.0.0/0)
     - ✅ Custom TCP (Port 8501) - Anywhere (for Streamlit)

7. **Configure Storage**
   - 30 GB gp3 (Free tier eligible: up to 30GB)

8. **Launch Instance**
   - Click "Launch Instance"
   - Wait for instance to be "Running"
   - Note the **Public IPv4 address**

---

### Step 2: Connect to EC2 Instance

#### On Windows (using PowerShell):

```powershell
# Navigate to your key location
cd ~\Downloads

# Set proper permissions (Windows)
icacls.exe egg-dashboard-key.pem /reset
icacls.exe egg-dashboard-key.pem /grant:r "$($env:USERNAME):(R)"
icacls.exe egg-dashboard-key.pem /inheritance:r

# Connect via SSH
ssh -i egg-dashboard-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

#### On Mac/Linux:

```bash
# Set proper permissions
chmod 400 egg-dashboard-key.pem

# Connect via SSH
ssh -i egg-dashboard-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

Replace `YOUR_EC2_PUBLIC_IP` with your actual EC2 public IP address.

---

### Step 3: Deploy Application

Once connected to EC2, run the deployment script:

```bash
# Download the deployment script
wget https://raw.githubusercontent.com/muddukrishna96/egg_identification_quality_dashboard/aws_deployment/deploy.sh

# Make it executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

**This script will:**
1. ✅ Update system packages
2. ✅ Install Python 3.10 and dependencies
3. ✅ Clone your GitHub repository
4. ✅ Create virtual environment
5. ✅ Install Python packages
6. ✅ Download model from GitHub Releases
7. ✅ Setup systemd services (backend + frontend)
8. ✅ Configure Nginx reverse proxy
9. ✅ Setup firewall rules
10. ✅ Start all services

**Deployment takes ~10-15 minutes**

---

### Step 4: Verify Deployment

After deployment completes:

1. **Check Services Status**
   ```bash
   sudo systemctl status egg-backend
   sudo systemctl status egg-frontend
   ```

2. **Access Dashboard**
   - Open browser: `http://YOUR_EC2_PUBLIC_IP`
   - You should see the Streamlit dashboard!

3. **Test API**
   - Backend API docs: `http://YOUR_EC2_PUBLIC_IP/api/docs`

---

## 🔄 Auto-Deploy from GitHub

### Option 1: Manual Updates

SSH to EC2 and run:

```bash
cd /home/ubuntu/egg_identification_quality_dashboard
./auto_update.sh
```

### Option 2: GitHub Actions (Automatic)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS EC2

on:
  push:
    branches: [ aws_deployment ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        env:
          PRIVATE_KEY: ${{ secrets.EC2_SSH_KEY }}
          HOST: ${{ secrets.EC2_HOST }}
          USER: ubuntu
        run: |
          echo "$PRIVATE_KEY" > private_key.pem
          chmod 600 private_key.pem
          ssh -o StrictHostKeyChecking=no -i private_key.pem ${USER}@${HOST} '
            cd /home/ubuntu/egg_identification_quality_dashboard
            ./auto_update.sh
          '
```

**Setup Secrets in GitHub:**
1. Go to: Settings → Secrets and variables → Actions
2. Add secrets:
   - `EC2_SSH_KEY`: Your private key content
   - `EC2_HOST`: Your EC2 public IP

### Option 3: Cron Job (Scheduled Updates)

Set up automatic updates every hour:

```bash
# On EC2, edit crontab
crontab -e

# Add this line
0 * * * * /home/ubuntu/egg_identification_quality_dashboard/auto_update.sh
```

---

## 📊 Monitoring & Logs

### View Service Logs

```bash
# Backend logs
sudo journalctl -u egg-backend -f

# Frontend logs
sudo journalctl -u egg-frontend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Service Management

```bash
# Restart services
sudo systemctl restart egg-backend
sudo systemctl restart egg-frontend
sudo systemctl restart nginx

# Stop services
sudo systemctl stop egg-backend
sudo systemctl stop egg-frontend

# Check status
sudo systemctl status egg-backend
sudo systemctl status egg-frontend
```

---

## 🔒 Security Best Practices

### 1. Update Security Group

After deployment, restrict SSH access:
- EC2 Console → Security Groups → `egg-dashboard-sg`
- Edit inbound rules
- SSH (Port 22): Change from "Anywhere" to "My IP"

### 2. Enable HTTPS (Optional but Recommended)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com
```

### 3. Setup CloudWatch Monitoring

- EC2 Console → Monitoring tab
- Enable detailed monitoring
- Set up alarms for CPU, Memory usage

---

## 💰 AWS Free Tier Limits

### What You Get (Free for 12 months):

| Resource | Free Tier Limit |
|----------|----------------|
| EC2 Instance | 750 hours/month (t2.micro) |
| Storage | 30 GB EBS |
| Data Transfer | 15 GB/month outbound |
| Elastic IP | 1 IP (while attached) |

### Cost Optimization Tips:

✅ Stop instance when not in use (doesn't count toward 750 hrs)
✅ Use only 1 Elastic IP (additional IPs cost money)
✅ Monitor data transfer usage
✅ Delete old snapshots
⚠️ Set up billing alerts!

---

## 🛠️ Troubleshooting

### Issue: Can't SSH to EC2

**Solution:**
1. Check security group allows SSH from your IP
2. Verify key file permissions (400)
3. Use correct username: `ubuntu` (not `ec2-user`)

### Issue: Services Not Starting

```bash
# Check logs for errors
sudo journalctl -u egg-backend -n 50
sudo journalctl -u egg-frontend -n 50

# Common fixes:
sudo systemctl daemon-reload
sudo systemctl restart egg-backend
sudo systemctl restart egg-frontend
```

### Issue: Model Download Fails

```bash
# Manual download
cd /home/ubuntu/egg_identification_quality_dashboard
mkdir -p model
wget -O model/best.pt https://github.com/muddukrishna96/egg_identification_quality_dashboard/releases/download/v1.0.0/best.pt
```

### Issue: Out of Memory

EC2 t2.micro has only 1GB RAM. If you face memory issues:

```bash
# Create swap file (2GB)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📱 Access Points

After deployment, your app is accessible at:

- **Dashboard**: `http://YOUR_EC2_IP` (via Nginx)
- **Streamlit Direct**: `http://YOUR_EC2_IP:8501`
- **Backend API**: `http://YOUR_EC2_IP/api/`
- **API Docs**: `http://YOUR_EC2_IP/api/docs`

---

## 🔄 Update Workflow

1. Make changes locally
2. Commit and push to `aws_deployment` branch
3. SSH to EC2 and run `./auto_update.sh`
4. Or wait for GitHub Actions to auto-deploy

---

## 🚨 Important Notes

1. **Free Tier Duration**: 12 months from account creation
2. **Always-On Cost**: After free tier, t2.micro costs ~$8-10/month
3. **Elastic IP**: Release if not using to avoid charges
4. **Backups**: Regularly backup your model and data
5. **Monitoring**: Set up CloudWatch billing alerts!

---

## 📞 Support Commands

```bash
# Complete restart
sudo systemctl restart egg-backend egg-frontend nginx

# Check disk space
df -h

# Check memory
free -h

# Check processes
top

# Update system
sudo apt-get update && sudo apt-get upgrade -y
```

---

## ✅ Deployment Checklist

- [ ] EC2 instance created and running
- [ ] Security group configured (SSH, HTTP, HTTPS)
- [ ] SSH connection successful
- [ ] Deployment script executed
- [ ] Services running (backend + frontend)
- [ ] Nginx configured
- [ ] Dashboard accessible via browser
- [ ] Model loaded successfully
- [ ] Test upload/predict functionality
- [ ] GitHub auto-deploy configured (optional)
- [ ] Billing alerts set up

---

## 🎉 Success!

Your dashboard should now be live at: **http://YOUR_EC2_IP**

Share this URL with your users!

**Estimated Total Time**: 30-45 minutes
**Monthly Cost**: $0 (within free tier)
