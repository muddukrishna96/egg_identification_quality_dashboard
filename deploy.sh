#!/bin/bash

# ============================================
# AWS EC2 Deployment Script
# Egg Tray Quality Inspection Dashboard
# ============================================

set -e  # Exit on error

echo "🚀 Starting deployment..."

# ============================================
# 1. Update System
# ============================================
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# ============================================
# 2. Install Python 3.10 and Dependencies
# ============================================
echo "🐍 Installing Python 3.10..."
sudo apt-get install -y python3.10 python3.10-venv python3-pip git

# ============================================
# 3. Install System Dependencies for OpenCV
# ============================================
echo "📸 Installing OpenCV dependencies..."
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev

# ============================================
# 4. Clone/Pull Repository
# ============================================
APP_DIR="/home/ubuntu/egg_identification_quality_dashboard"

if [ -d "$APP_DIR" ]; then
    echo "📥 Updating repository..."
    cd $APP_DIR
    git pull origin aws_deployment
else
    echo "📥 Cloning repository..."
    cd /home/ubuntu
    git clone -b aws_deployment https://github.com/muddukrishna96/egg_identification_quality_dashboard.git
    cd $APP_DIR
fi

# ============================================
# 5. Create Virtual Environment
# ============================================
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# ============================================
# 6. Install Python Dependencies
# ============================================
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# ============================================
# 7. Download Model (if not exists)
# ============================================
echo "🤖 Checking for model file..."
if [ ! -f "model/best.pt" ]; then
    echo "⬇️  Downloading model from GitHub Releases..."
    mkdir -p model
    
    # GitHub Release URL
    REPO="muddukrishna96/egg_identification_quality_dashboard"
    VERSION="v1.0.0"
    MODEL_URL="https://github.com/${REPO}/releases/download/${VERSION}/best.pt"
    
    # Download with wget
    wget -O model/best.pt "$MODEL_URL"
    
    if [ -f "model/best.pt" ]; then
        echo "✅ Model downloaded successfully"
    else
        echo "❌ Failed to download model"
        exit 1
    fi
else
    echo "✅ Model already exists"
fi

# ============================================
# 8. Setup Systemd Services
# ============================================
echo "⚙️  Setting up systemd services..."

# Backend Service
sudo tee /etc/systemd/system/egg-backend.service > /dev/null <<EOF
[Unit]
Description=Egg Tray Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend Service
sudo tee /etc/systemd/system/egg-frontend.service > /dev/null <<EOF
[Unit]
Description=Egg Tray Frontend Dashboard
After=network.target egg-backend.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# ============================================
# 9. Start Services
# ============================================
echo "🎬 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable egg-backend
sudo systemctl enable egg-frontend
sudo systemctl restart egg-backend
sudo systemctl restart egg-frontend

# ============================================
# 10. Setup Nginx (Optional - for production)
# ============================================
echo "🌐 Installing Nginx..."
sudo apt-get install -y nginx

sudo tee /etc/nginx/sites-available/egg-dashboard > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # Frontend (Streamlit)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/egg-dashboard /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# ============================================
# 11. Configure Firewall
# ============================================
echo "🔒 Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8501/tcp  # Streamlit (if direct access needed)
echo "y" | sudo ufw enable

# ============================================
# 12. Check Service Status
# ============================================
echo ""
echo "================================================"
echo "✅ Deployment Complete!"
echo "================================================"
echo ""
echo "📊 Service Status:"
sudo systemctl status egg-backend --no-pager | head -n 5
sudo systemctl status egg-frontend --no-pager | head -n 5
echo ""
echo "🌐 Access your dashboard at:"
echo "   http://$(curl -s ifconfig.me)"
echo ""
echo "📝 Useful commands:"
echo "   View backend logs:  sudo journalctl -u egg-backend -f"
echo "   View frontend logs: sudo journalctl -u egg-frontend -f"
echo "   Restart backend:    sudo systemctl restart egg-backend"
echo "   Restart frontend:   sudo systemctl restart egg-frontend"
echo ""
