#!/bin/bash
# EC2 instance setup script for iCal Viewer deployment

set -e

echo "Starting EC2 setup for iCal Viewer..."

# Update system
echo "Updating system packages..."
sudo yum update -y

# Install Docker
echo "Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install AWS CLI v2
echo "Installing AWS CLI v2..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws/

# Create application directory
echo "Setting up application directory..."
sudo mkdir -p /opt/ical-viewer
sudo chown ec2-user:ec2-user /opt/ical-viewer
cd /opt/ical-viewer

# Create data directory for persistent storage
mkdir -p data

echo "EC2 setup completed successfully!"
echo "Next steps:"
echo "1. Configure AWS credentials: aws configure"
echo "2. Copy docker-compose.prod.yml to /opt/ical-viewer/"
echo "3. Start the application: docker-compose -f docker-compose.prod.yml up -d"