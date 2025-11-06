#!/bin/bash

# ============================================
# Auto-Update Script for GitHub Integration
# Run this via GitHub webhook or cron job
# ============================================

set -e

APP_DIR="/home/ubuntu/egg_identification_quality_dashboard"

echo "🔄 Auto-update triggered..."

cd $APP_DIR

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin aws_deployment

# Activate virtual environment
source venv/bin/activate

# Update dependencies
echo "📚 Updating dependencies..."
pip install -r requirements.txt --upgrade

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart egg-backend
sudo systemctl restart egg-frontend

echo "✅ Update complete!"

# Log update
echo "$(date): Auto-update completed" >> /var/log/egg-dashboard-updates.log
